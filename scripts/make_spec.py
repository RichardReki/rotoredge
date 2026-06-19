"""Emit a RotorEdge StrategySpec JSON.

By default this is KEYLESS: it builds the spec (current target weights + backtest
provenance) from the committed snapshot. If a CMC key is available (env CMC_MCP_API_KEY)
or --x402 is passed, it ALSO attaches the LIVE-ONLY CMC Agent Hub overlay (dominance,
alt-season, Fear & Greed, funding, narratives) — clearly labelled, never backtested.

    python scripts/make_spec.py                 # keyless, backtest-only spec
    python scripts/make_spec.py --live          # + CMC overlay via API key (CMC_MCP_API_KEY)
    python scripts/make_spec.py --live --x402   # + CMC overlay via keyless x402
"""
from __future__ import annotations

import sys
import json
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rotoredge.config import load_config
from rotoredge.data import load_snapshot, snapshot_checksum
from rotoredge.backtest import Engine
from rotoredge import metrics as M
from rotoredge.spec import build_spec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/submission.yaml")
    ap.add_argument("--live", action="store_true", help="attach live CMC Agent Hub overlay")
    ap.add_argument("--x402", action="store_true", help="use keyless x402 transport for the overlay")
    ap.add_argument("--out", default="results/strategy_spec.json")
    args = ap.parse_args()

    cfg = load_config(args.config)
    snap = load_snapshot(cfg["snapshot_dir"])
    eng = Engine(snap, cfg)
    run = eng.run(start=cfg["backtest"]["start"])
    oos_metrics = {k: round(M.summarize(run.daily_returns)[k], 4) for k in ("sharpe", "max_drawdown", "cagr")}

    live_overlay = None
    if args.live:
        try:
            from rotoredge.mcp_client import CMCAgentHub, fetch_live_overlay
            hub = CMCAgentHub(keyless=args.x402)
            live_overlay = fetch_live_overlay(hub)
            print("[live] attached CMC Agent Hub overlay (LIVE-ONLY, not backtested)")
        except Exception as e:  # noqa: BLE001
            print(f"[live] overlay unavailable ({e}); emitting keyless backtest-only spec")

    spec = build_spec(snap, cfg, run, oos_metrics, snapshot_checksum(cfg["snapshot_dir"]), live_overlay)
    out = ROOT / args.out
    out.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    print(f"[spec] wrote {out}  (as_of {spec['as_of']}, regime {spec['regime']['state']}, gross {spec['exposure']['gross']})")
    print("[spec] target_weights:", spec["target_weights"])


if __name__ == "__main__":
    main()
