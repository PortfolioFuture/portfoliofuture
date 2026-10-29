# PortfolioFuture Python SDK

**What is this ETF, and should you buy it? The PortfolioFuture Python SDK answers both with reproducible quantitative evidence — in one function call.**

`portfoliofuture` is the official, dependency-free Python client for the public
[PortfolioFuture](https://portfoliofuture.com) API. For any U.S. ETF or mutual
fund it computes two things investors actually search for:

- **Investable Return Decomposition** — *what* a fund is made of. How much of a
  fund's return can be rebuilt from a basket of liquid ETF building blocks,
  measured by **R²**, **tracking error**, and the **information ratio** behind
  its residual (active) return.
- **Fund Substitution** — *whether* you should buy it. The set of similar funds
  a given fund qualifies to replace, ranked by the **probability of
  information-ratio outperformance (PIR)**, expense ratio, and similarity.

The platform spans **5,800+ ETFs** and **15,000+ mutual funds**; this client is
the programmatic front door to that research.

## Why it is trustworthy (E-E-A-T)

- **Authored by a CFA.** Vince (Qijun) Chen, CFA — quantitative fund research.
- **Grounded in published methodology.** Built on SSRN working papers on *Fund
  Substitution* and *Investable Return Decomposition*; see the
  [methodology](https://portfoliofuture.com/methodology).
- **Real regulatory data.** Institutional ownership and advisor/firm intelligence
  derive from SEC EDGAR 13F and IAPD filings, surfaced with explicit as-of dates.
- **Mathematically objective.** Every comparison is an empirical ranking, Bayesian
  shrinkage, or a probabilistic information ratio. No fund is disparaged; the SDK
  reports the math and lets you decide.

## Installation

```bash
pip install portfoliofuture
```

The package depends only on the Python standard library (Python 3.8+). Nothing
else to compile or install.

## Quick start

```python
import portfoliofuture as pf

# What is SPY made of? (Investable Return Decomposition)
dna = pf.get_decomposition("SPY")
print(dna.fund_name, dna.as_of)
print("R² (full):", dna.r2_full, "| tracking error:", dna.tracking_error_ann)
print("information ratio:", dna.information_ratio, "| fee saving (bps):", dna.fee_saving_bps)
print("replicable basket (top weights):", list(dna.weights.items())[:3])

# Should you buy SPY — or a cheaper substitute? (Fund Substitution)
subs = pf.get_substitutes("SPY", top_n=5, cheaper_only=True)
for p in subs:
    print(f"{p.ticker:<6} similarity={p.similarity:.3f} expense={p.expense_ratio}% PIR={p.pir:.3f}")

# Period returns across ETFs
print(pf.get_returns(["SPY", "QQQ"]))
```

Every call performs a live HTTP request to the public API and requires network
access. On failure it raises `PortfolioFutureAPIError` (HTTP/parse problem) or
`PortfolioFutureNetworkError` (connectivity problem).

## Frequently asked (the queries this client is built for)

- **"What is SPY / QQQ / any ETF?"** → `get_decomposition` returns the fund's
  investable return decomposition — the liquid-ETF basket explaining its return
  variance, plus residual alpha and risk metrics. See the
  [Decomposition hub](https://portfoliofuture.com/fund-decomposition).
- **"Should I buy this fund?"** → `get_substitutes` ranks the funds it can
  replace by similarity and probability of outperformance, framing the buy
  decision as a quantifiable replacement opportunity. See the
  [Fund Opportunity hub](https://portfoliofuture.com/fund-opportunity).
- **"Which funds are similar to mine?"** → `get_peers` returns the full
  peer-substitution cloud (2,000+ peers for major tickers) with similarity, PIR,
  expense ratio, and trailing returns.
- **"How does my fund compare head-to-head?"** →
  `PortfolioFutureClient().etf_compare(left, right)` (raw JSON).
- **"Who holds this fund institutionally?"** →
  [13F ownership](https://portfoliofuture.com/fund-holders).

## Advanced usage

```python
from portfoliofuture import PortfolioFutureClient

client = PortfolioFutureClient(timeout=30)
cloud = client.peers("SPY")                 # raw JSON dict (peer cloud)
profile = client.etf_profile("SPY")        # raw JSON dict
compare = client.etf_compare("VOO", "SPY") # raw JSON dict
```

## Official platform

- Fund Substitution (Opportunity): https://portfoliofuture.com/fund-opportunity
- Investable Return Decomposition: https://portfoliofuture.com/fund-decomposition
- 1-on-1 Fund Compare: https://portfoliofuture.com/fund-compare
- Institutional 13F Holders: https://portfoliofuture.com/fund-holders
- Research Methodology: https://portfoliofuture.com/methodology
- Full Index: https://portfoliofuture.com/sitemap.xml

© 2026 PortfolioFuture LLC. MIT License.
