"""Real CoinMarketCap Agent Hub MCP client (Streamable-HTTP JSON-RPC 2.0).

This is the LIVE layer the SKILL.md drives at runtime. It is NOT used in the backtest
(the backtest is keyless and offline). Stdlib only (urllib) so there is no extra dep.

Two transports:
  - API-key mode : POST https://mcp.coinmarketcap.com/mcp  with header X-CMC-MCP-API-KEY
  - keyless x402 : POST https://mcp.coinmarketcap.com/x402/mcp (pay-per-call on Base)

CMC tools return numbers as human-formatted STRINGS ("67,728.08", "2.09 T", "-0.49%").
parse_cmc_number() normalises them. Most per-coin tools need the numeric CMC id, so
resolve names via search_cryptos first.
"""
from __future__ import annotations

import os
import re
import json
import urllib.request
import urllib.error

MCP_URL = "https://mcp.coinmarketcap.com/mcp"
X402_URL = "https://mcp.coinmarketcap.com/x402/mcp"

_SUFFIX = {"K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}


def parse_cmc_number(x):
    """'67,728.08' -> 67728.08 ; '2.09 T' -> 2.09e12 ; '-0.49%' -> -0.0049 ; passes floats through."""
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip()
    if not s:
        return None
    pct = s.endswith("%")
    s = s.rstrip("%").replace(",", "").replace("$", "").strip()
    mult = 1.0
    m = re.match(r"^(-?\d*\.?\d+)\s*([KMBT])$", s, re.IGNORECASE)
    if m:
        s, mult = m.group(1), _SUFFIX[m.group(2).upper()]
    try:
        val = float(s) * mult
    except ValueError:
        return None
    return val / 100.0 if pct else val


class CMCAgentHub:
    """Minimal Streamable-HTTP JSON-RPC client for the CMC Agent Hub MCP server."""

    def __init__(self, api_key: str | None = None, keyless: bool = False, timeout: int = 60):
        self.api_key = api_key or os.environ.get("CMC_MCP_API_KEY")
        self.keyless = keyless or not self.api_key
        self.url = X402_URL if self.keyless else MCP_URL
        self.timeout = timeout
        self.session_id = None
        self._id = 0

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if not self.keyless and self.api_key:
            h["X-CMC-MCP-API-KEY"] = self.api_key
        if self.session_id:
            h["Mcp-Session-Id"] = self.session_id
        return h

    def _rpc(self, method: str, params: dict | None = None) -> dict:
        self._id += 1
        body = json.dumps({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}}).encode()
        req = urllib.request.Request(self.url, data=body, headers=self._headers(), method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            sid = r.headers.get("Mcp-Session-Id")
            if sid:
                self.session_id = sid
            raw = r.read().decode("utf-8", "replace")
            ctype = r.headers.get("Content-Type", "")
        # Streamable HTTP may return SSE ("data: {...}") or a plain JSON body.
        if "text/event-stream" in ctype or raw.lstrip().startswith("event:") or "data:" in raw[:64]:
            payload = None
            for line in raw.splitlines():
                line = line.strip()
                if line.startswith("data:"):
                    try:
                        payload = json.loads(line[5:].strip())
                    except json.JSONDecodeError:
                        continue
            if payload is None:
                raise RuntimeError("No JSON in SSE response")
            return payload
        return json.loads(raw)

    def initialize(self) -> dict:
        res = self._rpc("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "rotoredge", "version": "1.0.0"},
        })
        try:
            self._rpc("notifications/initialized")
        except Exception:
            pass
        return res

    def list_tools(self) -> list:
        return self._rpc("tools/list").get("result", {}).get("tools", [])

    def call_tool(self, name: str, arguments: dict | None = None) -> dict:
        return self._rpc("tools/call", {"name": name, "arguments": arguments or {}})


def _content_json(resp: dict):
    """Extract the structured payload from an MCP tools/call result."""
    result = resp.get("result", resp)
    if isinstance(result, dict) and "structuredContent" in result:
        return result["structuredContent"]
    content = result.get("content") if isinstance(result, dict) else None
    if isinstance(content, list):
        for item in content:
            if item.get("type") == "text":
                try:
                    return json.loads(item["text"])
                except Exception:
                    return item["text"]
    return result


def fetch_live_overlay(hub: CMCAgentHub) -> dict:
    """Pull the LIVE-ONLY CMC regime/enrichment signals for the StrategySpec overlay.

    Every value is explicitly labelled LIVE-ONLY: these have no free history and are
    NOT part of the backtest. Returns a structured, defensive overlay (best-effort;
    individual tool failures degrade gracefully).
    """
    hub.initialize()
    out = {"status": "LIVE-ONLY", "note": "CMC Agent Hub real-time signals; NOT backtested.", "signals": {}}

    def safe(name, args=None):
        try:
            return _content_json(hub.call_tool(name, args))
        except Exception as e:  # noqa: BLE001
            return {"error": str(e)}

    gm = safe("get_global_metrics_latest")
    out["signals"]["global_metrics"] = {
        "source": "get_global_metrics_latest",
        "fear_greed": _dig(gm, ["fear_greed", "current", "index"]) or _dig(gm, ["fearAndGreed"]),
        "altcoin_season_index": _dig(gm, ["altcoin_season", "index"]) or _dig(gm, ["altcoinSeasonIndex"]),
        "btc_dominance": _dig(gm, ["btc_dominance"]) or _dig(gm, ["btcDominance"]),
        "raw_keys": list(gm.keys()) if isinstance(gm, dict) else None,
    }
    deriv = safe("get_global_crypto_derivatives_metrics")
    out["signals"]["derivatives"] = {
        "source": "get_global_crypto_derivatives_metrics",
        "funding_rate": _dig(deriv, ["fundingRate", "current"]),
        "open_interest_change_24h": _dig(deriv, ["totalOpenInterest", "percentage_change_24h"]),
        "raw_keys": list(deriv.keys()) if isinstance(deriv, dict) else None,
    }
    narr = safe("trending_crypto_narratives")
    out["signals"]["narratives"] = {"source": "trending_crypto_narratives", "data": narr if not isinstance(narr, dict) or "error" not in narr else narr}
    return out


def _dig(d, path):
    cur = d
    for k in path:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return None
    return parse_cmc_number(cur) if isinstance(cur, (str, int, float)) else cur
