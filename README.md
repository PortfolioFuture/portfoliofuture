# PortfolioFuture Python SDK

**Programmatic access to institutional-grade ETF and mutual-fund intelligence: investable return decomposition, empirical fund opportunity, head-to-head comparability, and SEC 13F institutional ownership.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## What this is (and why it answers "should I buy this fund?")

`portfoliofuture` is the official, dependency-free Python client for the public
[PortfolioFuture](https://portfoliofuture.com) analytical API. It turns the
questions every allocator actually asks into one function call:

- **"What is this ETF, really?"** — decompose its return into liquid, repliable
  building blocks and measure the manager's genuine alpha (R², tracking error,
  information ratio).
- **"What is the opportunity?"** — find which incumbent funds a given fund can
  empirically replace, ranked by return similarity.
- **"Are these two funds comparable, and which is better?"** — a head-to-head
  similarity check with a cost-based verdict.
- **"Who actually holds this fund?"** — the institutional 13F ownership directory
  (4,800+ reporting institutions per core ETF).

Every function performs a live HTTP request to the public API or the PortfolioFuture
data CDN and returns parsed, typed results. **No data is bundled or fabricated.**

## Installation

```bash
pip install portfoliofuture
```

The package depends only on the Python standard library (Python 3.8+). There is
nothing else to install.

## Quick start

```python
import portfoliofuture as pf

# 1. What is this fund, really? (Investable Return Decomposition)
dna = pf.get_decomposition("SPY")
print(dna.fund_name, "information_ratio=", dna.information_ratio, "r2_full=", dna.r2_full)

# 2. What is the opportunity? (which funds can THIS fund replace)
for peer in pf.get_opportunity("SPY", top_n=5):
    print(peer.ticker, "similarity=", peer.similarity, "pir=", peer.pir)

# 3. Are two funds comparable, and which is better? (evaluate opportunity)
cmp = pf.evaluate_opportunity("SPY", "VOO")
print(cmp.comparable, cmp.better_ticker, cmp.better_reason)

# 4. Who holds it institutionally? (SEC 13F ownership, served from the data CDN)
holders = pf.get_holders("SPY")
print(holders.holder_firm_count, "institutions", holders.total_value_usd, "USD")
```

## Why it is trustworthy (E-E-A-T)

- **Authored by a CFA.** Vince (Qijun) Chen, CFA — former fund manager ($1B+ AUM, Morningstar 5-Star recognized).
- **Grounded in published research.** Algorithmic specifications originate from peer-reviewed SSRN working papers on *Fund Substitution* and *Investable Return Decomposition*; read the [quantitative research methodology](https://portfoliofuture.com/methodology).
- **Direct regulatory provenance.** Institutional ownership mappings derive from live [SEC EDGAR Form 13F and IAPD filings](https://portfoliofuture.com/fund-holders), published with verifiable as-of timestamps on the data CDN.
- **Mathematically objective.** Every comparison is an empirical ranking, empirical-Bayes shrinkage, or probabilistic information ratio P(IR > 0). No fund is disparaged; the SDK computes the math and lets allocators decide.

## Frequently asked queries (search & decision alignment)

- **"What is SPY / QQQ / any ETF?"**
  `pf.get_decomposition("SPY")` returns the fund's investable return decomposition — the liquid-ETF basket explaining its systematic return variance, plus active manager alpha.
  → *Explore the live model:* [Investable Return Decomposition Hub](https://portfoliofuture.com/fund-decomposition)

- **"Should I buy this fund? What is the opportunity?"**
  `pf.get_opportunity("SPY")` returns the funds this one can empirically replace, ranked by return similarity — the challenger's upside, not a slight against any incumbent.
  → *Check empirical rankings:* [Fund Opportunity Engine](https://portfoliofuture.com/fund-opportunity)

- **"Which funds are most similar to mine?"**
  `pf.get_peers("SPY")` calculates the empirical peer cloud from weekly-return covariance (13–260 weeks) and Bayesian shrinkage, rather than static Morningstar categories.
  → *Browse the peer cloud:* [Fund Opportunity Engine](https://portfoliofuture.com/fund-opportunity)

- **"Are these two funds comparable? Which is better?"**
  `pf.evaluate_opportunity("SPY", "VOO")` reports the empirical similarity and, when the two track the same exposure, the lower-cost share class.
  → *Compare side-by-side:* [Fund Compare Engine](https://portfoliofuture.com/fund-compare)

- **"Who holds this fund institutionally?"**
  `pf.get_holders("SPY")` reveals reported institutional positions across thousands of wealth managers, family offices, and bank trusts — the same [13F Fund Holders & Institutional Directory](https://portfoliofuture.com/fund-holders) on the platform.

## Web Platform & Research Engines

The Python client interfaces with the broader analytical ecosystem hosted at
[PortfolioFuture](https://portfoliofuture.com). You can explore full visual
datasets, historical time series, and institutional directories directly:

| Core Engine | Primary Use Case | Live Web Platform Link |
| :--- | :--- | :--- |
| **Fund Opportunity** | Discover behavioral peer funds and addressable incumbent AUM | [portfoliofuture.com/fund-opportunity](https://portfoliofuture.com/fund-opportunity) |
| **Return Decomposition** | Deconstruct active fund returns into liquid ETF factor building blocks | [portfoliofuture.com/fund-decomposition](https://portfoliofuture.com/fund-decomposition) |
| **1-on-1 Fund Compare** | Side-by-side empirical return similarity, tracking error, and TLH pairs | [portfoliofuture.com/fund-compare](https://portfoliofuture.com/fund-compare) |
| **13F Institutional Holders** | Map 4,800+ reporting institutions holding core market ETFs | [portfoliofuture.com/fund-holders](https://portfoliofuture.com/fund-holders) |
| **ETF Directory** | Systematic catalog of 5,800+ U.S. ETFs by asset class and duration | [portfoliofuture.com/etfs](https://portfoliofuture.com/etfs) |
| **Methodology & SSRN** | Mathematical framework, empirical-Bayes shrinkage, and formulas | [portfoliofuture.com/methodology](https://portfoliofuture.com/methodology) |
| **Sitemap & Registry** | Full canonical index of 32,000+ published quantitative research records | [portfoliofuture.com/sitemap.xml](https://portfoliofuture.com/sitemap.xml) |

## API reference

| Function | Endpoint | Returns |
| :--- | :--- | :--- |
| `get_decomposition(ticker)` | `/api/fund-dna/<ticker>` | `Decomposition` (R², tracking error, IR, fee saving) |
| `get_peers(ticker)` | `/api/fund-peers/<ticker>` | `PeerCloud` (full similarity graph) |
| `get_opportunity(ticker, top_n, min_similarity, cheaper_only)` | `/api/fund-peers/<ticker>` (ranked) | `List[Peer]` (funds this one can replace) |
| `evaluate_opportunity(left, right)` | `/api/etf-compare/<left>/<right>` | `Comparison` (similarity + better ticker) |
| `get_returns(tickers)` | `/api/etf/returns?tickers=<CSV>` | period returns |
| `get_holders(ticker)` | `data.portfoliofuture.com/tickers/ticker-<hex>.json` (CDN) | `Holders` (13F institutional ownership) |

## License

MIT — see [LICENSE](LICENSE).

© 2026 PortfolioFuture LLC.
