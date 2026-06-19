# RotorEdge — Design Spec

**Date:** 2026-06-20
**Target:** BNB Hack: AI Trading Agent Edition — Track 2 (Strategy Skills), $6k/3 winners + stackable "Best Use of CMC Agent Hub" $2k.
**Deadline:** 2026-06-21 12:00 UTC (= 20:00 Beijing). Submit several hours early.

## 0. One-liner

A CoinMarketCap **Skill** that, at each rebalance, ranks a **survivorship-bias-free, point-in-time** universe of BNB-eligible tokens by **volatility-adjusted cross-sectional momentum**, holds the top-K, and scales whole-book exposure with a **regime gate** — emitting a **backtestable StrategySpec JSON**, not live trades.

## 1. Why this wins (positioning)

Recon of 8 real Track-2 repos (incl. the 4 polished frontrunners undertow, strategy-forge, cmc-regime-skill, cmc-leverage-divergence) shows **the entire field is single-asset time-series timing** (price-vs-MA / Fear&Greed+funding regime gates, long/flat). Grep-confirmed: **none ranks or rotates across tokens.** The strategy lane is crowded; the rigor bar is high. RotorEdge differentiates on **two empty axes at once**:

1. **Cross-sectional ranking/rotation** — a genuinely different, academically-supported alpha class (crypto x-sec momentum, Sharpe ~1.0–1.2 in published studies). 0/8 competitors occupy it.
2. **Survivorship-bias-free, point-in-time universe** — even the most rigorous rival uses *today's* top-20 (the exact bias that inflates backtest returns several-fold). We reconstruct the tradable set as it existed at each date, including tokens that later died/delisted.

This maps to the 4 judging axes: **technical execution** (hardest backtest in the field), **originality** (new strategy class), **real-world relevance** (rotation across the actual BNB-eligible universe), **demo** (a rotation table that visibly shifts holdings demos better than an on/off gauge).

## 2. The honest data split (non-negotiable integrity rule)

CMC's 12 MCP tools are **all latest/snapshot/forward-looking** — no historical series. Therefore:

- **BACKTEST SPINE = keyless, reproducible, committed:** Binance daily OHLCV from `data.binance.vision` (checksum-verified) + alternative.me Fear&Greed (history to 2018). A judge re-runs with **zero credentials**.
- **CMC Agent Hub = the LIVE decision/enrichment layer** (the "Best Use of Agent Hub" showcase), never presented as backtest data.
- **Every signal is labeled `[BACKTESTED on <source, range>]` or `[LIVE-ONLY enhancement]`.** Never fabricate history. Disclose that single-venue Binance prices differ slightly from CMC's cross-exchange VWAP.

| Signal | Role | Source | Status |
|---|---|---|---|
| Vol-adjusted momentum (ranking factor) | core alpha | Binance OHLCV | **BACKTESTED** |
| BTC vs 100d MA (master risk-on/off) | regime | Binance OHLCV | **BACKTESTED** |
| Fear & Greed (exposure scalar) | risk | alternative.me | **BACKTESTED** |
| Altcoin-Season Index, BTC/ETH dominance | regime refine | CMC `get_global_metrics_latest` | LIVE-ONLY |
| Aggregate funding/OI extremity | crowding de-risk | CMC `get_global_crypto_derivatives_metrics` | LIVE-ONLY |
| Trending narratives | sector tilt | CMC `trending_crypto_narratives` | LIVE-ONLY |

## 3. Architecture (small, well-bounded units)

```
rotoredge/
├── skills/rotoredge/SKILL.md     # the deliverable Skill (drives CMC MCP tools live)
├── rotoredge/
│   ├── config.py      # load+validate configs/submission.yaml
│   ├── data.py        # keyless download + frozen snapshot load + SHA-256 manifest
│   ├── universe.py    # PIT survivorship-free top-N by trailing $-volume
│   ├── signals.py     # momentum factor, BTC regime, F&G scalar (all causal)
│   ├── costs.py       # 4-part BSC cost model
│   ├── backtest.py    # causal engine: rank -> weights -> t+1 open fill -> equity
│   ├── metrics.py     # Sharpe/Sortino/Calmar/maxDD+dur/CAGR/hit/payoff/turnover/PF/DSR
│   ├── walkforward.py # anchored WF param selection; train/validate/test-once
│   ├── spec.py        # StrategySpec JSON emitter (the IR deliverable)
│   ├── report.py      # plots + results/metrics.json + results-hash
│   └── mcp_client.py  # real CMC Agent Hub MCP client (Streamable-HTTP JSON-RPC)
├── scripts/{fetch_data.py, run_backtest.py, make_spec.py, verify.py}
├── configs/submission.yaml
├── data/snapshot/     # COMMITTED frozen OHLCV + F&G + manifest.json (SHA-256)
├── results/           # COMMITTED metrics.json, equity.png, heatmap.png, ...
├── dashboard/index.html
├── tests/
├── Makefile / reproduce.sh
└── README.md, LICENSE(MIT), THIRD_PARTY.md
```

## 4. Data layer

- **Universe candidates:** a curated list of BNB-eligible / major BEP-20 tokens that trade as Binance `*USDT` spot pairs, **deliberately including historically-prominent tokens that later collapsed/delisted** (e.g. LUNA, FTT, WAVES) to be survivorship-bias-free. Stablecoins and pegged assets (USDT/USDC/DAI/USDD/USDe/FDUSD, XAUt, WBTC) are excluded from the *tradable* set.
- **Download:** monthly daily klines per symbol from `data.binance.vision/data/spot/monthly/klines/<SYM>/1d/`, concatenated; CSV cols → use **close** and **quote_asset_volume** (USDT $-volume, col index 7). Symbols/months that 404 are simply absent (a token that wasn't listed yet, or is delisted) — this is the survivorship-free mechanism.
- **F&G:** `api.alternative.me/fng/?limit=0&format=json` (full daily history).
- **Snapshot:** write `data/snapshot/prices.parquet`, `dollar_volume.parquet`, `fng.parquet`, and `manifest.json` with per-file SHA-256 + as-of date + source URLs + row/col counts. The backtest reads **only** the snapshot (no network at run time).

## 5. Universe selection (survivorship-bias-free, point-in-time)

At each monthly rebalance date *t*:
1. Eligible = tokens with a valid close at *t* **and** ≥ `min_history_days` of prior history (so momentum is defined). A token that delisted before *t* is absent → correctly excluded; a token that lists later only appears from its listing → no look-ahead.
2. Rank eligible by **trailing 30d mean dollar-volume as of *t*** (liquidity screen; the correct screen for a rotation you could actually execute, and fully keyless — no historical market-cap reconstruction needed).
3. Universe(t) = top-`universe_n` by that $-volume.

Disclose explicitly: $-volume is used instead of market cap as a deliberate, liquidity-appropriate, keyless, point-in-time choice.

## 6. Strategy logic

- **Ranking factor:** volatility-adjusted trailing momentum = `mean(daily_log_return over L days, skip last S days) / std(daily_return over L days)`. Skip-recent (`S`≈5) avoids short-term reversal. Computed on **closed bars only**.
- **Selection/weighting:** long top-`K` of Universe(t) by factor; **equal-weight** (config option: inverse-vol). Long/flat spot, no leverage, no shorting.
- **Regime gate (master switch, BACKTESTED proxy):** if BTC close < its `regime_ma` (100d) MA → **risk-OFF**: book to cash (0 invested, or BNB per config). Else risk-ON.
- **Exposure scalar (BACKTESTED):** Fear&Greed maps to a multiplier in [`fng_floor`, 1.0] (trim in Extreme Greed; full in fear) applied to gross exposure.
- **LIVE-ONLY overlays (skill runtime only, labeled):** CMC alt-season/dominance refine risk-on/off; funding extremity trims crowded names; narratives tilt sectors. **Not in the backtest.**
- **Rebalance:** monthly (config); **turnover deadband** — skip trades whose target-vs-current weight change < `deadband` to cut churn/cost.

## 7. Backtest engine (causality is sacred)

- Decide using data through **close *t*** (all features shifted ≥1 bar); **execute at the next bar's OPEN (*t+1*)**. Returns accrue open→open thereafter; unit-tested.
- **Costs** applied on traded notional **before** any metric (see §8).
- No global normalization: any scaling fit on train only. Indicators computed causally; warm-up region dropped from both signal and trades.
- Output: daily strategy returns (net), equity curve, weights panel, trade log, turnover series.

## 8. BSC cost model (`costs.py`)

Per fill on traded notional `Δ`:
1. **Swap fee:** `fee_bps` (default 25 bps = PancakeSwap V3 0.25% volatile tier).
2. **AMM price impact / slippage:** constant-product proxy `impact ≈ Δ / (pool_depth)`; capacity-capped — config `pool_depth_usd` per name; impact grows with trade-size-to-liquidity.
3. **Slippage buffer:** `buffer_bps` (default 10, stress to 30) for adverse fill/MEV.
4. **Gas:** fixed `gas_usd` per swap (default $0.20; BSC is cheap & ~flat) → dominates and kills tiny/high-freq trades.

Round-trip ≈ 2×(fee+impact+buffer) + 2×gas. Report a **0 / base / 2×-stress** sensitivity table + breakeven cost level + turnover-driven annual cost drag (bps).

## 9. Validation & metrics

- **Walk-forward (anchored/expanding):** optimize {`L`, `K`} (and maybe `fng_floor`) on in-sample, **freeze**, evaluate on the immediately-following OOS block, roll, stitch. Report the **stitched OOS** curve as the headline.
- **Three-way split:** train (fit) / validate (select) / **test (touched once)**. State the test was evaluated a single time.
- **Metrics:** Sharpe, Sortino, Calmar, max drawdown + duration, CAGR/total return, hit rate + payoff ratio, turnover + cost-drag bps, profit factor, n_trades — **reported IS vs OOS side by side**.
- **Multiple-testing honesty:** count variants tried; report **Deflated Sharpe Ratio**.
- **Baselines (same period + same costs):** BNB HODL, BTC HODL, equal-weight-hold-universe, naive top-K-by-raw-return.
- **Per-regime split:** bull / bear / chop sub-period stats.

## 10. Deliverables ↔ judging

- **StrategySpec JSON** (`spec.py`): `schema_version, as_of, universe{method:"PIT top-N by trailing $-vol", n, members[]}, rebalance_freq, ranking_factor{name,L,skip,vol_adjust}, top_k, weighting, regime{state, gate{source, live_only}}, exposure_scalar, target_weights[], rules, risk_limits{max_per_name, drawdown_guard}, cost_model, backtest_provenance{source_urls, symbols, date_range, snapshot_sha256}, signal_labels[]`.
- **SKILL.md:** official frontmatter (name, description w/ `Trigger:`, license, compatibility, user-invocable, `allowed-tools` = **only** the CMC MCP tools actually called); numbered workflow resolving ids → live regime → quotes → derivatives → narratives → rank → emit spec; `parse_cmc_number` rules; tool-failure fallback; `[BACKTESTED]/[LIVE-ONLY]` labels. A **real** `mcp_client.py` hits the hosted CMC MCP (no declared-but-unused tools — judges grep for that).
- **Reproducibility:** `make repro` (or `python scripts/verify.py`) reads only the committed snapshot, re-runs the full WF, writes `results/metrics.json` + plots, prints data-checksum + results-hash and **asserts** they equal committed reference values → byte-identical, keyless.
- **Dashboard:** static `dashboard/index.html` (no server) reading exported JSON — rotation table shifting across a regime flip, equity vs baselines, regime ribbon.
- **Demo:** ~60s script (cold-open headline → one-command repro hash → StrategySpec + live CMC call).

## 11. Risks & mitigations

- *Look-ahead in x-sec plumbing* → shift features ≥1 bar to t+1 open; fit scalers train-only; drop warm-up; unit-test the shift.
- *Underperform HODL on raw return in a bull* → lead with risk-adjusted (Calmar/Sortino/maxDD) + breadth; show per-regime; admit it.
- *Too few rebalances* → monthly over multi-year/multi-regime so n clears ~30–50; flag n.
- *Declared-but-unused MCP tools* → whitelist only tools the workflow calls; make live path genuinely call CMC.
- *Repro drift* → pin deps+seeds, single entrypoint reads only snapshot, assert checksum+results-hash.
- *Capacity fantasy on thin alts* → AMM impact term caps per-name size; state honest capacity ceiling.

## 12. Scope discipline (must-ship order)

Momentum core + PIT survivorship-free universe + causal backtest + WF/metrics/baselines + reproducibility + honesty artifacts → SKILL.md + live MCP client → StrategySpec → README → dashboard → demo script. Fallbacks if tight: 30-token universe; smaller param grid; dashboard before video.

## 13. User-only blocking actions (cannot be automated)

CMC free API key (LIVE path only; `.env`, gitignored) · DoraHacks BUIDL submission + confirm exact form fields/special-prize label · record/upload demo video · push public repo before 2026-06-21 12:00 UTC.
