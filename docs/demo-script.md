# RotorEdge — ~60s demo video script

Goal: in one minute, land (1) the differentiation, (2) the rigor, (3) the keyless reproducibility.
Record at 1080p+; show the terminal and `dashboard/index.html`. Keep cuts tight.

---

**[0:00–0:08] Cold open — the differentiation.**
*Screen: dashboard equity chart with the regime ribbon + rotation heatmap.*
> "Every other strategy-skill times one coin. RotorEdge is the only one that *rotates* — each month it
> ranks BNB-eligible tokens by volatility-adjusted momentum and holds the strongest, risk-managed."

**[0:08–0:20] The honest edge.**
*Screen: baselines/ablations table.*
> "Majors beat alts this cycle — we show that. But against the fair benchmark, a naive alt basket lost
> 16% a year with an 87% drawdown. RotorEdge turns that into *positive* return at *half* the drawdown.
> The ablations prove it's the selection plus the risk overlay."

**[0:20–0:34] Rigor a quant judge can trust.**
*Screen: scroll robustness cards — IS→OOS, cost sensitivity, Deflated Sharpe, per-regime.*
> "This is walk-forward out-of-sample, after PancakeSwap costs, deflated for the nine configs we tried —
> Deflated Sharpe 0.70. The universe is survivorship-bias-free: dead coins like WAVES and FTT are still
> in history. And no look-ahead — we unit-test that changing a future price can't move past P&L."

**[0:34–0:46] Keyless one-command reproduction.**
*Screen: terminal.*
```
python scripts/run_backtest.py
python scripts/verify.py
```
*Show `verify.py` printing the green checks and "PASS — reproduce byte-identically … no API key".*
> "A judge re-runs everything from a committed data snapshot — no API key — and gets identical numbers,
> hash-checked."

**[0:46–0:58] The Skill + CoinMarketCap Agent Hub.**
*Screen: `skills/rotoredge/SKILL.md` frontmatter, then `make_spec.py --live` output / the spec JSON.*
> "The deliverable is a CoinMarketCap Skill. The backtest is keyless; the CMC Agent Hub is the *live*
> layer — dominance, alt-season, funding crowding, narratives — every signal labelled BACKTESTED or
> LIVE-ONLY. It outputs a backtestable StrategySpec. It never places a trade."

**[0:58–1:02] Close.**
*Screen: README title.*
> "RotorEdge: the rotation no one else built, with evidence anyone can reproduce."

---

### Shot checklist
- [ ] Dashboard open, data loaded (run `python scripts/run_backtest.py` first so `dashboard/data.js` exists).
- [ ] Terminal font large enough to read; clear scrollback before recording the reproduce/verify run.
- [ ] Show the green `verify.py` PASS line.
- [ ] Show `SKILL.md` frontmatter (name, Trigger, allowed-tools) and `results/strategy_spec.json` (signal_labels).
- [ ] Keep total ≤ ~65s; captions on (judging weights demo/presentation).
