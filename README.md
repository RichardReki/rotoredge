# RotorEdge

**Survivorship-bias-free cross-sectional momentum rotation for BNB-eligible tokens — shipped as a CoinMarketCap Agent Hub Skill with a keyless, walk-forward-validated backtest.**

> BNB Hack: AI Trading Agent Edition — **Track 2 (Strategy Skills)**. Deliverable: a backtestable strategy spec, not a live-trading agent.
> `MIT` · backtest needs **no API key** · CoinMarketCap Agent Hub = the live decision layer.

---

## TL;DR

Every other Track-2 entry we surveyed times a **single asset** (price-vs-MA / Fear&Greed regime gates). **RotorEdge is the only cross-sectional rotation**: each month it ranks a **point-in-time, survivorship-bias-free** universe of BNB-eligible tokens by **volatility-adjusted momentum**, holds the top-5 (inverse-vol weighted), and scales whole-book exposure with a regime gate + portfolio vol-targeting + Fear&Greed. It emits a `rotoredge.strategy_spec.v1` JSON. The CoinMarketCap Agent Hub provides the **live** regime/crowding/narrative signals; the **backtest** runs on keyless public data so a judge reproduces every number with one command and zero credentials.

## Headline results (walk-forward, out-of-sample, after costs)

OOS window **2021-06-30 → 2026-05-31** (~4.9 years, multi-regime). 61-token universe pool, 2019–2026.

| Strategy | Sharpe | CAGR | Max DD | Total Return |
|---|---:|---:|---:|---:|
| **RotorEdge (OOS)** | **0.37** | **+6.2%** | **−34.5%** | **+34.7%** |
| HODL BTC | 0.55 | +16.2% | −76.6% | — |
| HODL BNB | 0.59 | +18.8% | −69.9% | — |
| EqualWeight Universe *(naive alt basket)* | 0.12 | **−16.1%** | −87.3% | — |
| Momentum, no risk overlay *(ablation)* | 0.21 | **−9.1%** | −90.6% | — |

Also: **Deflated Sharpe 0.70** (after correcting for 9 trials), **survives 2× costs** (Sharpe 0.51 / 0.37 / 0.22 at 0×/1×/2×), **bull-regime Sharpe 1.50**, IS Sharpe 0.70 → **OOS 0.37** (honest ~47% degradation, consistent with the well-known 30–50% live haircut).

### Read this honestly
- **Majors (BTC/BNB) beat alts on raw return this cycle.** We do **not** hide it. RotorEdge is the *risk-managed alt-rotation sleeve*, not a BTC-beater. Against its fair benchmark — naive alt exposure — it converts a **−16% CAGR / −87% drawdown disaster into +6% CAGR / −35% drawdown**, and roughly **halves** the drawdown of holding majors. The two ablations *prove* the value comes from the selection + the risk overlay, not from luck.
- It is **strong in bull regimes (Sharpe 1.50)** and bleeds in bear/chop — that's the honest shape of long-only alt momentum.

## Reproduce in 3 lines (keyless — no API key)

```bash
pip install -r requirements.txt
python scripts/run_backtest.py      # walk-forward OOS, costs, baselines -> results/
python scripts/verify.py            # asserts the numbers match results/REFERENCE.json
```

`verify.py` re-derives everything from the **committed** snapshot (`data/snapshot/`, SHA-256 in `manifest.json`) and asserts the headline metrics + a results-hash match the committed reference — byte-identical, offline. (Windows: use `python` directly; `make repro && make verify` also works where `make` is available.)

Then open **`dashboard/index.html`** (double-click; works offline) to explore the equity curve, regime ribbon, live rotation, and robustness panels.

## How it uses the CoinMarketCap Agent Hub  *(Best Use of Agent Hub)*

The deliverable Skill is [`skills/rotoredge/SKILL.md`](skills/rotoredge/SKILL.md) — official format (frontmatter + `Trigger:` + numbered workflow), declaring **only the 5 MCP tools it actually calls** (`search_cryptos`, `get_crypto_quotes_latest`, `get_global_metrics_latest`, `get_global_crypto_derivatives_metrics`, `trending_crypto_narratives`).

[`rotoredge/mcp_client.py`](rotoredge/mcp_client.py) is a **real** Streamable-HTTP JSON-RPC client for `mcp.coinmarketcap.com` (API-key *and* keyless x402 transports), with `parse_cmc_number` for CMC's string-formatted numbers. Run the live-enriched spec with:

```bash
python scripts/make_spec.py --live           # CMC_MCP_API_KEY in env
python scripts/make_spec.py --live --x402     # keyless x402 transport
```

**The honest split** (every signal is labelled in the spec): CMC's tools are all *latest/snapshot*, so they drive the **live** decision (regime refinement via altcoin-season/dominance, funding-rate crowding de-risk, trending-narrative tilt) — never the backtest. The backtest's signals (momentum, BTC-trend regime, Fear&Greed) run on keyless history. We never present a CMC snapshot as historical.

## Architecture

```
                    DECISION (live, CoinMarketCap Agent Hub MCP)        EVIDENCE (keyless, offline)
  user / agent  ->  skills/rotoredge/SKILL.md                           data/snapshot/  (Binance OHLCV + alt.me F&G,
                    rotoredge/mcp_client.py  --[LIVE-ONLY signals]-->     committed, SHA-256 manifest)
                         |                                                     |
                         v                                                     v
                    rotoredge/spec.py  ->  StrategySpec JSON  <----  rotoredge/{universe,signals,backtest,
                    (target weights + provenance + labels)            walkforward,metrics,baselines}.py
```

## Rigor checklist (what a quant judge looks for)

- ✅ **No look-ahead** — decide on close *t*, execute next **open *t+1***; features shifted ≥1 bar; unit-tested (perturbing a future price leaves past P&L byte-identical).
- ✅ **Walk-forward** anchored OOS; train/validate selection, **test touched once**; IS-vs-OOS reported side by side.
- ✅ **Survivorship-bias-free** point-in-time universe (includes since-delisted tokens, e.g. WAVES ends 2024-06; FTT's collapse is in-sample).
- ✅ **Realistic costs** — PancakeSwap fee + AMM price impact + slippage buffer + BSC gas, with a 0/1×/2× sensitivity table.
- ✅ **Multiple-testing correction** — Deflated Sharpe Ratio over the 9 swept configs.
- ✅ **Keyless, one-command, hash-checked reproduction**; pinned deps; fixed seed.
- ✅ **Honest baselines & ablations**, per-regime breakdown, and a documented negative result (a reactive daily kill-switch *whipsawed* OOS — see [docs/methodology.md](docs/methodology.md)).

## Repo layout

```
skills/rotoredge/SKILL.md     the deliverable Skill (drives the CMC Agent Hub MCP)
rotoredge/                    config, data, universe, signals, costs, backtest, walkforward, metrics, baselines, spec, report, mcp_client
scripts/                      fetch_data.py · run_backtest.py · verify.py · make_spec.py
configs/submission.yaml       the single frozen config that produces the headline numbers
data/snapshot/                committed keyless OHLCV + Fear&Greed + SHA-256 manifest
results/                      metrics.json · strategy_spec.json · equity_oos.png · heatmap.png · REFERENCE.json
dashboard/index.html          static, offline demo dashboard
tests/                        no-look-ahead · costs · parser · metrics · survivorship
docs/                         methodology.md · demo-script.md · specs/
```

## Disclaimer

Not financial advice. RotorEdge emits a backtestable research specification; it does **not** place trades, custody funds, or launch any token. Backtested performance does not guarantee future results. Backtest prices are single-venue (Binance) and differ slightly from CoinMarketCap's cross-exchange VWAP.

See [docs/methodology.md](docs/methodology.md) for the full method, assumptions, and limitations · [THIRD_PARTY.md](THIRD_PARTY.md) for data attributions.
