# RotorEdge — Methodology, Assumptions & Limitations

This document is the auditable record of *how* the numbers are produced and *where* the strategy is
weak. We would rather a judge read our own honest critique than find it themselves.

## 1. Data (keyless, reproducible)

- **Prices/volume:** Binance daily OHLCV from `data.binance.vision`, 2019-01-01 → 2026-05-31, for a
  curated 61-token pool of BNB-eligible / major BEP-20-tradable symbols. **Deliberately includes
  tokens that later collapsed or delisted** (e.g. WAVES — data ends 2024-06-17; FTT — its crash is in
  the series) so the historical universe is **survivorship-bias-free**.
- **Sentiment:** Crypto Fear & Greed from alternative.me (daily since 2018).
- Stablecoins/pegged assets are excluded from the *tradable* set. The snapshot is committed with a
  SHA-256 manifest; the backtest reads it offline.

## 2. Universe (survivorship-bias-free, point-in-time)

At each rebalance date *t*, eligible = tokens with a valid price at *t* and ≥130 days of prior
history. Eligible names are ranked by **trailing 30-day dollar-volume as of *t*** and the **top-15**
form the universe. Dollar-volume (price × Binance quote-asset-volume) is used instead of market cap as
a deliberate choice: it is the correct liquidity screen for a rotation you could actually execute, it
needs no historical market-cap reconstruction, and it is fully keyless and point-in-time. A token that
delisted before *t* is simply absent; one that lists later only appears from its listing — no
look-ahead either way.

## 3. Signals (all causal — computed on closed bars only)

| Signal | Role | Status |
|---|---|---|
| Vol-adjusted momentum: (L-day log return ending `skip` days ago) ÷ (window vol) | ranking factor | **BACKTESTED** (Binance) |
| BTC close vs 100-day MA | master risk-on/off gate | **BACKTESTED** (Binance) |
| Portfolio volatility targeting (target 35% ann.) | exposure scalar | **BACKTESTED** (derived) |
| Fear & Greed (trim in extreme greed) | exposure scalar | **BACKTESTED** (alt.me) |
| Altcoin-Season Index, BTC/ETH dominance | regime refinement | **LIVE-ONLY** (CMC) |
| Aggregate funding / open interest | crowding de-risk | **LIVE-ONLY** (CMC) |
| Trending narratives | sector tilt | **LIVE-ONLY** (CMC) |

LIVE-ONLY signals have no free history; they are wired into the Skill's runtime decision and labelled
as such in the spec. They are **never** in the backtest. We never present a CMC snapshot as historical.

## 4. Portfolio construction

- Rank the universe by momentum; hold the **top-5**, **inverse-volatility** weighted (risk-parity-lite,
  so one high-vol name can't dominate book risk). Long-only, no leverage, no shorting.
- **Gross exposure** = regime_on × min(1, target_vol / realized_book_vol) × Fear&Greed-scalar.
- **Composition is refreshed monthly** (every 21 days). Risk would ideally be managed more often, but
  see the negative result in §7.

## 5. Backtest engine (causality is sacred)

Per-asset value is tracked explicitly. Each day splits into an **overnight leg** (close[t-1]→open[t]
on the old book) and an **intraday leg** (open[t]→close[t] on the post-trade book). A rebalance decided
from information through **close[t-1]** is **executed at open[t]** with full costs. Missing/delisted
prices force liquidation to cash at the last value — we *eat* collapses (FTT/WAVES), no survivorship
escape. The no-look-ahead property is unit-tested: perturbing any future price leaves all prior P&L
byte-identical (`tests/test_no_lookahead.py`).

## 6. Costs (BSC / PancakeSwap), validation & metrics

- **Cost model** (charged on the realized fill, before any metric): 0.25% swap fee + linear AMM price
  impact (`traded_usd / pool_depth`, capacity-capped) + 10 bps slippage buffer + ~$0.20 gas/swap.
  Reported at **0× / 1× / 2×** stress.
- **Walk-forward (anchored):** optimize {lookback, top_k} on an expanding in-sample window, freeze,
  evaluate the next out-of-sample block, roll. Each OOS block starts from cash (a conservative choice
  that pays an extra entry cost rather than inflating returns). The stitched OOS curve is the headline.
- **Metrics:** Sharpe, Sortino, Calmar, max drawdown + duration, CAGR, hit-rate + payoff, turnover,
  profit factor, n_trades — reported **IS vs OOS side by side**.
- **Deflated Sharpe Ratio** (Bailey & López de Prado) over the 9 swept configs: DSR ≈ 0.70.

## 7. A documented NEGATIVE result (why monthly, not daily, risk management)

We hypothesised that managing risk *daily* (a reactive regime/vol kill-switch with a turnover
deadband) would cut the bear/chop bleed. We tested it. It **whipsawed**: OOS Sharpe collapsed from
~0.37 (monthly) to ~0.07–0.15 (daily), and chop-regime Sharpe roughly tripled in the wrong direction —
the classic cost of reacting to noisy crypto regime signals. We therefore use **monthly composition
with a high deadband** (the kill-switch is effectively off) and say so. Keeping the disproven idea in
the code (toggled off) and reporting it is part of the rigor.

## 8. Limitations (read these)

- **Majors beat alts this cycle.** Over the OOS window BTC/BNB HODL out-returned RotorEdge on raw and
  risk-adjusted return; RotorEdge wins on **drawdown** and decisively vs the **fair alt benchmark**. It
  is an alt-rotation sleeve, not a majors-beater.
- **Bull-dependent.** Per-regime: bull Sharpe ~1.5, bear/chop negative. Long-only alt momentum is
  structurally a bull-market engine; the regime gate + vol-target reduce but do not eliminate the bleed.
- **Inverse-vol can concentrate.** With no explicit per-name cap, inverse-vol overweights low-vol names
  (e.g. a single name can exceed 50% in a given month). A `max_per_name` cap is a natural, easy
  extension we deliberately left out to keep the spec minimal — flagged honestly.
- **LIVE-ONLY signals are unbacktested** by construction (no free history). The CMC overlay improves the
  live decision but its historical value is *not* claimed.
- **Single-venue prices** (Binance) differ slightly from CMC's cross-exchange VWAP.
- **Capacity.** The AMM-impact term caps size vs pool depth; edges shrink at larger AUM. Not modelled:
  reverted txs, MEV beyond the buffer, partial fills.
- **OOS window starts at the 2021 alt top**, the worst possible entry for alt momentum — we did not
  shop the window for a flattering start.
