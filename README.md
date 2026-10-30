# PortfolioFuture Python SDK

**Pull live fund research straight from [PortfolioFuture](https://portfoliofuture.com): what a fund can replace, how much of it is real skill vs. cheap ETFs, how two funds stack up, and who owns it.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## What you can ask it

`portfoliofuture` is the official, dependency-free Python client for PortfolioFuture's
public API. It answers the four questions investors actually ask — with live numbers,
not bundled ones:

- **"Should I buy this fund?"** — Depends what you hold. See **which funds it can
  replace**, and how much money is sitting in those funds.
- **"Is this fund's performance real skill?"** — Rebuild the fund out of cheap, liquid
  ETFs. What you can't rebuild is the manager's real alpha.
- **"How do two funds stack up?"** — Put them side by side: do they move together, and
  which one reliably wins?
- **"Who owns it?"** — The institutions (13F) holding the funds it can replace — the
  people you'd actually call.

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

# 1. Should I buy this fund? -> which funds can it replace?
for peer in pf.get_opportunity("SPY", top_n=5):
    print(peer.ticker, "moves like SPY:", peer.similarity,
          "| SPY beats it:", peer.target_conviction)

# 2. Is its performance real skill? -> rebuild it from cheap ETFs.
dna = pf.get_decomposition("SPY")
print("replicable:", dna.r2_full, "| leftover alpha:", dna.residual_ir_annualized)

# 3. How do two funds stack up? -> similar, and which one wins?
cmp = pf.evaluate_opportunity("SPY", "VOO")
print(cmp.comparable, "winner:", cmp.better_ticker, "—", cmp.better_reason)

# 4. Who owns the funds it can replace? (SEC 13F)
h = pf.get_holders("SPY")
print(h.holder_firm_count, "institutions,", h.total_value_usd, "USD")
```

## The two ideas behind it (in plain words)

**What a fund can replace — "Fund Substitution Index" (FSI).**
Two funds count as "this one can replace that one" when they move together *and* this
one reliably beats the other. We call that score FSI. PortfolioFuture flags a
replacement when FSI is above 80. Under the hood it's just two things: how similarly
the funds move (return similarity) + how often this fund outperforms (its
probability of a positive information ratio, P(IR>0)).

> One gotcha the SDK handles for you: the raw "P(IR>0)" in the data is the *other*
> fund's win rate over this one. The SDK flips it (`1 - pir`) so you get **this
> fund's** own edge — `peer.target_conviction` — instead of accidentally reading it
> backwards.

**Real skill vs. cheap ETFs — "Return Decomposition."**
Take a basket of low-cost, liquid ETFs and rebuild the fund's return. The part the
ETFs explain is what anyone can replicate; whatever is left over is the manager's
real alpha. That's all it is — no "factor alpha," just "how much can I rebuild, and
how much is genuine skill."

## Why trust it (E-E-A-T)

- **Written by a CFA.** Vince (Qijun) Chen, CFA — former fund manager ($1B+ AUM, Morningstar 5-Star recognized).
- **Based on published research.** The method comes from peer-reviewed SSRN working papers on *Fund Substitution* and *Investable Return Decomposition*; see the [methodology](https://portfoliofuture.com/methodology).
- **Straight from filings.** Institutional ownership comes from live [SEC EDGAR Form 13F and IAPD filings](https://portfoliofuture.com/fund-holders), each with a verifiable as-of date.
- **Just the math.** Every call is an empirical ranking or a probability P(IR>0). No fund is put down; the SDK does the math and lets you decide.

## The questions people actually search

- **"Should I buy this fund?"**
  `pf.get_opportunity("SPY")` → which funds it can replace, and how reliably it beats them.
  → [Fund Opportunity](https://portfoliofuture.com/fund-opportunity)

- **"What is this fund really doing?"**
  `pf.get_decomposition("SPY")` → rebuild it from cheap ETFs; what's left is real alpha.
  → [Return Decomposition](https://portfoliofuture.com/fund-decomposition)

- **"Which funds move like mine?"**
  `pf.get_peers("SPY")` → the funds whose returns track this one, with how close and how often it wins.
  → [Fund Opportunity](https://portfoliofuture.com/fund-opportunity)

- **"How do two funds compare?"**
  `pf.evaluate_opportunity("SPY", "VOO")` → do they move together, and which one reliably wins?
  → [Fund Compare](https://portfoliofuture.com/fund-compare)

- **"Who owns the funds it can replace?"**
  `pf.get_holders("SPY")` → the institutions and wealth advisors holding them.
  → [13F Fund Holders](https://portfoliofuture.com/fund-holders)

## The whole platform

The Python client taps into the same research shown on
[PortfolioFuture](https://portfoliofuture.com), where you can see it as charts and
full histories:

| What it does | In plain words | Where |
| :--- | :--- | :--- |
| **Fund Opportunity** | See what a fund can replace, and how much money sits in those funds | [fund-opportunity](https://portfoliofuture.com/fund-opportunity) |
| **Return Decomposition** | Rebuild a fund from cheap ETFs — what's replicable vs. real alpha | [fund-decomposition](https://portfoliofuture.com/fund-decomposition) |
| **Fund Compare** | Two funds side by side: do they move together, which one wins | [fund-compare](https://portfoliofuture.com/fund-compare) |
| **13F Institutional Holders** | Who owns the funds your fund can replace | [fund-holders](https://portfoliofuture.com/fund-holders) |
| **ETF Directory** | Every U.S. ETF, organized | [etfs](https://portfoliofuture.com/etfs) |
| **Methodology & SSRN** | The math behind the ratings | [methodology](https://portfoliofuture.com/methodology) |
| **Sitemap** | Index of everything published | [sitemap.xml](https://portfoliofuture.com/sitemap.xml) |

## API reference

| Function | What you get |
| :--- | :--- |
| `get_opportunity(ticker)` | Which funds this one can replace, ranked by how similar it moves × how reliably it beats them |
| `evaluate_opportunity(left, right)` | Whether two funds move together, and which one reliably wins |
| `get_decomposition(ticker)` | How much of the fund you can rebuild from cheap ETFs vs. leftover alpha |
| `get_peers(ticker)` | The full list of funds whose returns track this one |
| `get_returns(tickers)` | Period returns for one or more funds |
| `get_holders(ticker)` | The institutions (13F) holding it |

## License

MIT — see [LICENSE](LICENSE).

© 2026 PortfolioFuture LLC.
