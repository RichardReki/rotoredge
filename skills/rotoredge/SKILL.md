---
name: rotoredge
description: |
  Generates a RotorEdge cross-sectional momentum ROTATION strategy spec for BNB-eligible tokens.
  Ranks a survivorship-bias-free, point-in-time universe by volatility-adjusted momentum, holds the
  top-K (inverse-vol weighted), and scales whole-book exposure with a regime gate (BTC trend),
  portfolio volatility targeting, and the CoinMarketCap Fear & Greed / dominance / funding signals.
  Emits a backtestable StrategySpec JSON — it does NOT place trades. Use for portfolio rotation,
  "which alts to hold now", risk-managed altcoin exposure, or building a backtestable rotation skill.
  Trigger: "rotoredge", "rotation strategy", "which alts to hold", "cross-sectional momentum", "rebalance my alts", "/rotoredge"
license: MIT
compatibility: ">=1.0.0"
user-invocable: true
allowed-tools:
  - mcp__cmc-mcp__search_cryptos
  - mcp__cmc-mcp__get_crypto_quotes_latest
  - mcp__cmc-mcp__get_global_metrics_latest
  - mcp__cmc-mcp__get_global_crypto_derivatives_metrics
  - mcp__cmc-mcp__trending_crypto_narratives
---

# RotorEdge — Cross-Sectional Momentum Rotation Skill

Produce a **RotorEdge StrategySpec**: a ranked, risk-managed rotation across BNB-eligible tokens.
The strategy logic is **backtested offline on keyless data** (Binance OHLCV + alternative.me Fear &
Greed; see the repo's `scripts/run_backtest.py`, walk-forward validated). This skill is the **live
decision layer**: it refreshes the universe + ranking from current data and enriches the exposure
decision with CoinMarketCap Agent Hub signals that have no free history.

> **Honesty contract.** Every signal below is labelled **[BACKTESTED]** (reproducible on committed
> keyless data) or **[LIVE-ONLY]** (CMC real-time enrichment, NOT in the backtest). Never present a
> CMC `*_latest` snapshot as historical. The spec you emit is research, **not financial advice**, and
> places no trades.

## Prerequisites

Configure the CoinMarketCap Agent Hub MCP. API-key mode:

```json
{
  "mcpServers": {
    "cmc-mcp": {
      "url": "https://mcp.coinmarketcap.com/mcp",
      "headers": { "X-CMC-MCP-API-KEY": "your-api-key" }
    }
  }
}
```

Keyless x402 mode: use `https://mcp.coinmarketcap.com/x402/mcp` and drop the header (pay-per-call on
Base). Get an API key at https://pro.coinmarketcap.com/login. If tools return connection errors, ask
the user to set this up.

**Data gotcha:** CMC tools return numbers as strings, sometimes with commas / `B`,`M`,`K`,`T` suffixes
/ `%` (e.g. `"67,728.08"`, `"2.09 T"`, `"-0.49%"`). Parse to float (strip `, $ %`, expand suffixes,
divide percents by 100) before any math. Per-coin tools need the numeric CMC **id** — resolve names
with `search_cryptos` first (BTC=1, ETH=1027, BNB=1839).

## Core Principle

Pick the basket monthly, manage risk by exposure. The ranking is a backtested factor; the CMC live
layer adjusts *how much* to hold and flags crowding/regime — it never invents historical performance.

## Workflow

### Step 1 — Resolve the universe ids  [BACKTESTED universe rule]
The point-in-time universe = the top-N (default 15) BNB-eligible tokens by trailing 30-day
dollar-volume (survivorship-bias-free; see repo). For a live spec, take the current candidate
symbols and call `search_cryptos` for each to get numeric CMC ids.

### Step 2 — Pull current prices & momentum inputs  [BACKTESTED factor]
Call `get_crypto_quotes_latest` with the comma-separated ids. The ranking factor is volatility-
adjusted trailing momentum (≈ 90-day return ÷ 90-day vol, skip last 5 days), computed from price
history. For an exact, reproducible ranking run `python scripts/make_spec.py` in the repo (it uses the
committed keyless snapshot). Rank, take the **top-K (default 5)**, weight **inverse-volatility**.

### Step 3 — Read the master regime gate  [BACKTESTED: BTC vs 100d MA] + [LIVE-ONLY refine]
Risk-ON only when BTC trades above its 100-day moving average (backtested switch). Refine with
`get_global_metrics_latest`:
- **Fear & Greed** → exposure scalar (trim in extreme greed). *(F&G is also BACKTESTED via alternative.me.)*
- **Altcoin-Season Index** and **BTC/ETH dominance** → **[LIVE-ONLY]** confirm whether alts are in favour.

### Step 4 — Crowding de-risk  [LIVE-ONLY]
Call `get_global_crypto_derivatives_metrics`. If aggregate **funding rate** is extreme (crowded longs)
or 24h **open-interest** change is very large, reduce gross exposure. (No free history → live overlay only.)

### Step 5 — Sector tilt  [LIVE-ONLY]
Call `trending_crypto_narratives` to note which sectors are hot; optionally tilt within the top-K toward
in-favour narratives. Label clearly as a live, non-backtested adjustment.

### Step 6 — Size the book  [BACKTESTED: vol targeting]
Gross exposure = regime_on × min(1, target_vol(0.35) / realized_book_vol) × fear_greed_scalar, then
apply the LIVE-ONLY crowding haircut. Long-only, no leverage.

### Step 7 — Emit the StrategySpec JSON
Output the spec with: universe (PIT method + members), ranking_factor, selection (top_k, inverse_vol),
regime state, exposure (gross + drivers), target_weights, risk_limits, cost_model, signal_labels
(BACKTESTED vs LIVE-ONLY), and backtest_provenance (keyless sources, date range, snapshot SHA-256,
out-of-sample metrics). Schema: `rotoredge.strategy_spec.v1` (see repo `results/strategy_spec.json`).

## Output template

```json
{
  "schema_version": "rotoredge.strategy_spec.v1",
  "as_of": "YYYY-MM-DD",
  "regime": {"state": "risk_on|risk_off", "gate": {"source": "BTC vs 100d MA", "live_only": false}},
  "exposure": {"gross": 0.00, "drivers": {"vol_target": 0.35, "fear_greed": 0, "altseason_live": 0, "funding_live": 0.0}},
  "target_weights": {"<SYMBOL>": 0.00},
  "signal_labels": [{"signal": "...", "status": "BACKTESTED|LIVE-ONLY", "source": "..."}],
  "backtest_provenance": {"snapshot_sha256": "...", "out_of_sample": {"sharpe": 0.0, "max_drawdown": 0.0}},
  "disclaimer": "Not financial advice. Backtestable research spec; does not place trades."
}
```

## Error handling

- **search_cryptos finds nothing** → report the unresolved symbol, skip it, continue with the rest.
- **A tool times out / 429** → retry once; if still failing, emit the spec with that signal marked
  `unavailable` and keep its label LIVE-ONLY (never substitute a fabricated value).
- **No MCP connection** → you can still emit the BACKTESTED core spec from the repo
  (`python scripts/make_spec.py`); the LIVE-ONLY overlay is simply omitted and noted.

## Reproduce the evidence

The backtested numbers in any spec are regenerated, keyless, with:
`python scripts/run_backtest.py` (walk-forward OOS, costs, baselines) — no API key required.
