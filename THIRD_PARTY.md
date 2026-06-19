# Third-party data & dependencies

RotorEdge is MIT-licensed. It uses the following third-party resources.

## Data (backtest — keyless, committed to `data/snapshot/`)

- **Binance public market data** — daily OHLCV (open/close/quote-asset-volume) from
  `https://data.binance.vision/` (public bulk archive; no API key). Used as the price/volume
  spine for the backtest. © Binance; used under their public data terms for research.
- **Crypto Fear & Greed Index** — `https://api.alternative.me/fng/` (keyless, full daily history
  since 2018-02). Used as the sentiment exposure scalar. © alternative.me.

Single-venue (Binance) prices differ slightly from CoinMarketCap's cross-exchange VWAP; this is
disclosed and the backtest is provider-independent by design.

## Data & tooling (live layer — optional, not used in the backtest)

- **CoinMarketCap Agent Hub MCP** — `https://mcp.coinmarketcap.com/mcp` (API key) and
  `…/x402/mcp` (keyless x402). Provides the live regime/crowding/narrative enrichment signals.
  API key from https://pro.coinmarketcap.com/login. © CoinMarketCap.
- **Official CMC skill format** — `github.com/openCMC/skills-for-ai-agents-by-CoinMarketCap` (MIT)
  was used as the SKILL.md format reference.

## Python libraries

`pandas`, `numpy`, `scipy`, `matplotlib`, `PyYAML` (see `requirements.txt`). Downloads use only the
Python standard library (`urllib`), so no `requests` dependency.

## Methods (academic references)

- Deflated / Probabilistic Sharpe Ratio — Bailey & López de Prado (2014), *The Deflated Sharpe Ratio*.
- Cross-sectional momentum — standard factor-investing literature; applied here to crypto.
