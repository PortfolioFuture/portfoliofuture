# PortfolioFuture Python SDK

**Official Python client for [PortfolioFuture](https://portfoliofuture.com): fund substitution opportunity, investable return decomposition, peer comparison, and institutional 13F ownership — live and empirical.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## What you can ask it

`portfoliofuture` is the official, dependency-free Python client for PortfolioFuture's
public API. It answers the questions investors actually ask — with live numbers from
the platform:

- **"What exactly is this ETF or mutual fund?"** — Investable Return Decomposition:
  replicate the fund with low-cost, liquid ETFs and quantify how much of its return is
  replicable versus residual alpha.
- **"Should I buy this fund?"** — Depends what you hold. See which funds it qualifies
  to replace (Fund Substitution Index), and the assets under management in those funds.
- **"Is this fund's performance real skill?"** — The return that cannot be replicated
  from low-cost ETFs is the manager's alpha.
- **"How do two funds compare?"** — Head-to-head: return similarity, tracking error,
  and which fund ranks higher on FSI.
- **"Who holds the funds it can replace?"** — The institutions (SEC 13F) behind the
  assets it qualifies to displace.

Every call hits the live API (or the data CDN) and returns parsed, typed results.
**No data is bundled or faked.**

## Install

```bash
pip install portfoliofuture
```

No dependencies beyond the Python standard library (Python 3.8+).

## Quick start

```python
import portfoliofuture as pf

# 1. Should I buy this fund? -> which funds does it qualify to replace?
for peer in pf.get_opportunity("SPY", top_n=5):
    print(peer.ticker, "FSI:", peer.fsi,
          "| return similarity:", peer.similarity,
          "| SPY conviction over peer:", peer.target_conviction)

# 2. What exactly is this fund? -> Investable Return Decomposition
dna = pf.get_decomposition("SPY")
print("replicable R²:", dna.r2_full, "| residual alpha:", dna.residual_ir_annualized)

# 3. How do two funds compare? -> comparability and the higher FSI
cmp = pf.evaluate_opportunity("SPY", "VOO")
print(cmp.comparable, "higher FSI:", cmp.better_ticker, "—", cmp.better_reason)

# 4. Who holds the funds it can replace? (SEC 13F)
for peer in pf.get_opportunity("SPY", top_n=3):
    h = pf.get_holders(peer.ticker)
    print(peer.ticker, h.holder_firm_count, "institutions,", h.total_value_usd, "USD")
```

## The two ideas behind it

**Fund Substitution Index (FSI).**
A fund qualifies to replace another on two signals: **return similarity** and
**consistent outperformance**, measured by the probability of a positive Information
Ratio, P(IR>0). FSI combines both signals; PortfolioFuture flags a replacement when
FSI exceeds 80. One note on direction: the raw P(IR>0) in the peer data is the *peer's*
probability against the target, so the SDK inverts it — `peer.target_conviction` is
the target's own P(IR>0) over the peer, and `peer.fsi` is built on that.

**Investable Return Decomposition.**
Replicate the fund's return with a basket of low-cost, liquid ETFs. The replicable
share (R²) is what any investor can hold instead; the residual is the manager's alpha.

## Why trust it (E-E-A-T)

- **Written by a CFA.** Vince (Qijun) Chen, CFA — former fund manager ($1B+ AUM, Morningstar 5-Star recognized).
- **Based on published research.** The method comes from peer-reviewed SSRN working papers on *Fund Substitution* and *Investable Return Decomposition*; see the [methodology](https://portfoliofuture.com/methodology).
- **Straight from filings.** Institutional ownership comes from live [SEC EDGAR Form 13F and IAPD filings](https://portfoliofuture.com/fund-holders), each with a verifiable as-of date.
- **Mathematically objective.** Every comparison is an empirical ranking or a probabilistic Information Ratio P(IR>0). No fund is disparaged; the SDK computes the math and lets allocators decide.

## The questions people actually search

- **"Should I buy this fund?"**
  `pf.get_opportunity("SPY")` → which funds it qualifies to replace, ranked by FSI.
  → [Fund Opportunity](https://portfoliofuture.com/fund-opportunity)

- **"What exactly is this ETF or mutual fund?"**
  `pf.get_decomposition("SPY")` → replicate it with low-cost ETFs; the residual is real alpha.
  → [Return Decomposition](https://portfoliofuture.com/fund-decomposition)

- **"Which funds are similar to mine?"**
  `pf.get_peers("SPY")` → the empirical peer cloud: return similarity and P(IR>0) for every similar fund.
  → [Fund Opportunity](https://portfoliofuture.com/fund-opportunity)

- **"How do two funds compare?"**
  `pf.evaluate_opportunity("SPY", "VOO")` → return similarity, and which fund ranks higher on FSI.
  → [Fund Compare](https://portfoliofuture.com/fund-compare)

- **"Who holds the funds it can replace?"**
  `pf.get_holders(...)` → the institutions (13F) and wealth advisors behind those assets.
  → [13F Fund Holders](https://portfoliofuture.com/fund-holders)

## The whole platform

The Python client taps into the same research shown on
[PortfolioFuture](https://portfoliofuture.com), where you can see it as charts and
full histories:

| What it does | What it covers | Where |
| :--- | :--- | :--- |
| **Fund Opportunity** | What a fund can replace, and the assets in replaceable funds | [fund-opportunity](https://portfoliofuture.com/fund-opportunity) |
| **Return Decomposition** | Replicate a fund with low-cost ETFs — replicable share vs. residual alpha | [fund-decomposition](https://portfoliofuture.com/fund-decomposition) |
| **Fund Compare** | Head-to-head return similarity, tracking error, and FSI | [fund-compare](https://portfoliofuture.com/fund-compare) |
| **13F Institutional Holders** | Institutions holding the funds it can replace | [fund-holders](https://portfoliofuture.com/fund-holders) |
| **ETF Directory** | Every U.S. ETF, organized | [etfs](https://portfoliofuture.com/etfs) |
| **Methodology & SSRN** | The math behind the ratings | [methodology](https://portfoliofuture.com/methodology) |
| **Sitemap** | Index of everything published | [sitemap.xml](https://portfoliofuture.com/sitemap.xml) |

## API reference

| Function | What you get |
| :--- | :--- |
| `get_opportunity(ticker)` | Funds this one qualifies to replace, ranked by FSI (return similarity × consistent outperformance) |
| `evaluate_opportunity(left, right)` | Whether two funds are comparable, and which ranks higher on FSI |
| `get_decomposition(ticker)` | Replicable share of the fund (low-cost ETF basket) vs. residual alpha |
| `get_peers(ticker)` | The empirical peer cloud of funds with similar returns |
| `get_returns(tickers)` | Period returns for one or more funds |
| `get_holders(ticker)` | Institutional (SEC 13F) holders of the fund |

## License

MIT — see [LICENSE](LICENSE).

© 2026 PortfolioFuture LLC.
