# DoraHacks BUIDL — ready-to-paste submission pack

Hackathon: **BNB Hack: AI Trading Agent Edition** · submit at https://dorahacks.io/hackathon/bnbhack-twt-cmc
Deadline: **2026-06-21 12:00 UTC (20:00 Beijing)** — submit several hours early.

---

## Field-by-field (map to whatever the form shows)

| Form field | Value to paste |
|---|---|
| **BUIDL name** | RotorEdge |
| **Tagline / short intro** | The only cross-sectional momentum *rotation* strategy skill — survivorship-bias-free, walk-forward validated, and reproducible with zero API keys. |
| **Track** | Track 2 — Strategy Skills |
| **Special prize to target** | **Best Use of CoinMarketCap Data & Signal** ($2,000) |
| **Source code (public repo)** | https://github.com/RichardReki/rotoredge |
| **Demo video** | https://youtu.be/CTZBxZjM84U |
| **Live demo / website** | (optional) the static dashboard `dashboard/index.html` in the repo (open offline) |
| **Tags** | quant, trading-strategy, cross-sectional-momentum, backtesting, CoinMarketCap, Agent-Hub, MCP, BNB |
| **Team** | RichardReki |
| **Description** | paste the block below |

---

## Description (paste this block)

**RotorEdge — survivorship-bias-free cross-sectional momentum rotation for BNB-eligible tokens.**

Every other Strategy-Skill entry we surveyed times a **single asset** (price-vs-MA / Fear & Greed regime gates). **RotorEdge is the only cross-sectional *rotation*:** each month it ranks a **point-in-time, survivorship-bias-free** universe of BNB-eligible tokens by **volatility-adjusted momentum**, holds the top-5 (inverse-volatility weighted), and risk-manages whole-book exposure with a BTC-trend regime gate, portfolio volatility targeting, and CoinMarketCap's Fear & Greed signal. It emits a backtestable `rotoredge.strategy_spec.v1` JSON — it does **not** place trades.

**Headline results — walk-forward, out-of-sample, after PancakeSwap costs** (OOS 2021-06-30 → 2026-05-31, ~4.9y, multi-regime; 61-token pool, 2019–2026):

| Strategy | Sharpe | CAGR | Max DD |
|---|--:|--:|--:|
| **RotorEdge (OOS)** | **0.37** | **+6.2%** | **−34.5%** |
| HODL BTC | 0.55 | +16.2% | −76.6% |
| HODL BNB | 0.59 | +18.8% | −69.9% |
| EqualWeight Universe (naive alt basket) | 0.12 | −16.1% | −87.3% |
| Momentum, no risk overlay (ablation) | 0.21 | −9.1% | −90.6% |

Also: **Deflated Sharpe 0.70** (corrected for 9 trials), survives **2× costs** (Sharpe 0.51 / 0.37 / 0.22 at 0×/1×/2×), bull-regime Sharpe **1.50**, IS 0.70 → OOS 0.37 (honest ~47% degradation).

**We report this honestly:** majors (BTC/BNB) out-returned alts this cycle — we don't hide it. RotorEdge is the *risk-managed alt-rotation sleeve*: against its fair benchmark (naive alt exposure) it turns a −16% CAGR / −87% drawdown disaster into +6% / −34.5%, and roughly halves the drawdown of holding majors. Two ablations prove the value comes from the selection + the risk overlay, not luck.

**Best Use of CoinMarketCap Data & Signal.** The deliverable is a CoinMarketCap Skill (`skills/rotoredge/SKILL.md`, official format, declaring only the 5 MCP tools it calls). `rotoredge/mcp_client.py` is a real Streamable-HTTP JSON-RPC client for the CMC Agent Hub (API-key *and* keyless x402), with `parse_cmc_number` for CMC's string-formatted numbers. The honest split: CMC's tools are all *latest/snapshot*, so they drive the **live** decision (alt-season + dominance regime refinement, funding-rate crowding de-risk, trending-narrative tilt) and are labelled **LIVE-ONLY** in the spec; the **backtest** runs on keyless public history (Binance + alternative.me) labelled **BACKTESTED**. We never present a CMC snapshot as historical.

**Reproduce every number with zero API keys, in 3 lines:**
```
pip install -r requirements.txt
python scripts/run_backtest.py     # walk-forward OOS, costs, baselines
python scripts/verify.py           # asserts results match the committed reference (hash-checked)
```
The backtest reads only a committed, SHA-256-pinned data snapshot. Rigor: no look-ahead (decide on close, execute next open; unit-tested that a future price can't change past P&L), walk-forward with a test set touched once, survivorship-bias-free universe (dead coins like WAVES/FTT are in history), realistic BSC cost model, Deflated Sharpe, and a documented *negative* result (a reactive daily kill-switch whipsawed OOS, so we use monthly rebalancing). All rigor tests pass.

**Not financial advice.** Emits a research spec; places no trades, custodies no funds, launches no token.

- Code: https://github.com/RichardReki/rotoredge
- Methodology & limitations: `docs/methodology.md` · Skill: `skills/rotoredge/SKILL.md` · Spec: `results/strategy_spec.json`

---

## How it meets the 4 judging criteria (for your talking points)

- **Technical execution** — walk-forward OOS, no-look-ahead (unit-tested), survivorship-bias-free PIT universe, realistic BSC costs + sensitivity, Deflated Sharpe, keyless hash-checked one-command reproduction.
- **Originality** — the only cross-sectional rotation in a field of single-asset timers; the only survivorship-bias-free universe; a documented negative result.
- **Real-world relevance** — rotates across the actual BNB-eligible token set; honestly framed as the risk-managed alt-rotation sleeve with a clear user (alt allocators) and a real edge over naive alt exposure.
- **Demo** — offline static dashboard (equity vs baselines, regime ribbon, live rotation heatmap, robustness panels) + a tight ~60s video.

## Reminders before you submit
- [ ] Select **Track 2 (Strategy Skills)** and target **Best Use of CoinMarketCap Data & Signal**.
- [ ] Paste the repo link: https://github.com/RichardReki/rotoredge
- [ ] Add the demo video link once recorded.
- [ ] Submit before **2026-06-21 12:00 UTC**.
