"""MCP server exposing PortfolioFuture fund research to LLM clients.

Optional component of the SDK — requires the ``mcp`` package
(``pip install portfoliofuture[mcp]``). The core library stays dependency-free.

Run with either entry point:
    portfoliofuture-mcp
    python -m portfoliofuture.mcp

Product semantics (do not "fix" back):
  * Public verbs are opportunity / evaluate — never "substitution".
    get_fund_opportunity answers "which funds can THIS fund replace?"
    (the challenger's upside).
  * FSI (Fund Substitution Index) = return similarity x consistent
    outperformance P(IR>0). Raw ``pir`` in the data is the PEER's P(IR>0)
    against the target; the target's own edge is ``1 - pir``.
  * Investable Return Decomposition = replicate the fund with low-cost,
    liquid ETFs -> replicable share (R-squared) vs. residual alpha.
    Never "factor alpha" / "factor building blocks".
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from mcp.server.mcpserver import MCPServer as _Server  # mcp >= 2
except ImportError:  # pragma: no cover - mcp 1.x
    try:
        from mcp.server.fastmcp import FastMCP as _Server  # mcp 1.x
    except ImportError as exc:
        raise ImportError(
            "The PortfolioFuture MCP server requires the 'mcp' package. "
            "Install it with: pip install portfoliofuture[mcp]"
        ) from exc

from .api import (
    evaluate_opportunity,
    get_decomposition,
    get_fund_url,
    get_holders,
    get_opportunity,
)
from .exceptions import PortfolioFutureAPIError, PortfolioFutureError
from .models import Holders, Peer

mcp = _Server(
    "PortfolioFuture",
    instructions=(
        "PortfolioFuture live fund research: investable return decomposition, "
        "fund substitution opportunity (FSI), head-to-head comparison, and "
        "SEC 13F institutional ownership. All figures are empirical and live; "
        "each tool also returns the official web URL for deeper reading."
    ),
)


def _peer_row(p: Peer, target: str) -> Dict[str, Any]:
    """Serialize one opportunity target for an LLM-friendly payload."""
    return {
        "ticker": p.ticker,
        "name": p.name,
        "is_mutual_fund": p.is_mutual_fund,
        "fsi": p.fsi,
        "return_similarity": p.similarity,
        "pir_peer_over_target": p.pir,
        "target_conviction_over_peer": p.target_conviction,
        "expense_ratio": p.expense_ratio,
        "aum": p.aum,
        "return_1y": p.return_1y,
        "compare_url": get_fund_url(p.ticker, "compare"),
    }


def _holders_summary(h: Holders, max_rows: int = 10) -> Dict[str, Any]:
    """Serialize the head of one 13F holder document."""
    rows = []
    for r in h.rows[:max_rows]:
        rows.append({k: r.get(k) for k in (
            "firm_key", "firm_name", "value_usd", "shares", "report_period",
        ) if k in r})
    return {
        "ticker": h.ticker,
        "fund_name": h.fund_name,
        "holder_firm_count": h.holder_firm_count,
        "total_value_usd": h.total_value_usd,
        "last_report_period": h.last_report_period,
        "top_holders": rows,
        "holders_url": get_fund_url(h.ticker, "holders"),
    }


def _error(ticker: str, tool: str, exc: Exception) -> Dict[str, Any]:
    return {
        "error": f"{tool} failed for {ticker}: {exc}",
        "ticker": ticker,
    }


@mcp.tool()
def get_fund_decomposition(ticker: str) -> Dict[str, Any]:
    """Investable Return Decomposition for one ETF or mutual fund.

    Replicates the fund's return with a basket of low-cost, liquid ETFs and
    quantifies the replicable share (R-squared) versus the manager's residual
    alpha, with tracking error, information ratio, and fee-saving figures.

    Use when users ask:
    - "What exactly is this ETF or mutual fund?"
    - "How much of this fund can I rebuild from cheap, liquid ETFs?"
    - "Is this fund's performance real skill?"
    """
    t = ticker.upper().strip()
    try:
        dna = get_decomposition(t)
        return {
            "ticker": t,
            "fund_name": dna.fund_name,
            "as_of": dna.as_of,
            "replicable_share_r2": dna.r2_full,
            "tracking_error_annualized": dna.tracking_error_ann,
            "information_ratio": dna.information_ratio,
            "residual_alpha_annualized": dna.residual_alpha_ann,
            "residual_ir_annualized": dna.residual_ir_annualized,
            "fee_saving_bps": dna.fee_saving_bps,
            "expense_ratio": dna.expense_ratio,
            "replicable_etf_basket": dna.weights,
            "research_url": get_fund_url(t, "decomposition"),
        }
    except PortfolioFutureError as exc:
        return _error(t, "get_fund_decomposition", exc)


@mcp.tool()
def get_fund_opportunity(
    ticker: str,
    top_n: int = 5,
    min_fsi: float = 0.0,
) -> Dict[str, Any]:
    """Funds this fund qualifies to replace — its substitution opportunity.

    The challenger's view: given a fund, which incumbent funds can it displace?
    Ranked by FSI (Fund Substitution Index) = return similarity x consistent
    outperformance P(IR>0) — the target must move like the incumbent AND
    reliably beat it. The web platform flags a replacement at FSI > 80
    (min_fsi=0.80 here on the 0-1 scale).

    Use when users ask:
    - "Should I buy this fund?" (depends what they already hold)
    - "What can this fund replace?"
    - "Which similar funds does it outrank?"
    """
    t = ticker.upper().strip()
    try:
        peers = get_opportunity(t, top_n=top_n, min_fsi=min_fsi)
        return {
            "target_ticker": t,
            "opportunity_count": len(peers),
            "fsi_definition": "return similarity x consistent outperformance P(IR>0)",
            "qualifying_line": "FSI > 80 (min_fsi=0.80)",
            "funds_it_can_replace": [_peer_row(p, t) for p in peers],
            "opportunity_url": get_fund_url(t, "opportunity"),
        }
    except PortfolioFutureError as exc:
        return _error(t, "get_fund_opportunity", exc)


@mcp.tool()
def compare_funds(left_ticker: str, right_ticker: str) -> Dict[str, Any]:
    """Head-to-head comparison of two ETFs or mutual funds.

    Reports return similarity, tracking error, whether the pair is comparable,
    and which fund ranks higher on FSI (Fund Substitution Index — return
    similarity x consistent outperformance). Both directions are scored
    (fsi_left, fsi_right) and the higher FSI ranks as better.

    Use when users ask:
    - "Compare SPY vs VOO" / "QQQ vs QQQM"
    - "Are these two funds comparable?"
    - "Can I use this pair for tax-loss harvesting?"
    - "Which of these two funds should I hold?"
    """
    left = left_ticker.upper().strip()
    right = right_ticker.upper().strip()
    try:
        c = evaluate_opportunity(left, right)
        return {
            "pair": f"{left} vs {right}",
            "left_ticker": c.left_ticker,
            "right_ticker": c.right_ticker,
            "return_similarity": c.similarity,
            "annual_correlation": c.annual_correlation,
            "tracking_error_annualized": c.tracking_error_ann,
            "comparable": c.comparable,
            "fsi_left_replaces_right": c.fsi_left,
            "fsi_right_replaces_left": c.fsi_right,
            "better_ticker": c.better_ticker,
            "better_reason": c.better_reason,
            "pir_peer_over_target": c.pir,
            "left_expense_ratio": c.left_expense_ratio,
            "right_expense_ratio": c.right_expense_ratio,
            "compare_url": get_fund_url(left, "compare"),
        }
    except PortfolioFutureError as exc:
        return _error(f"{left}/{right}", "compare_funds", exc)


@mcp.tool()
def get_institutional_holders(ticker: str, max_rows: int = 10) -> Dict[str, Any]:
    """SEC 13F institutional ownership of the fund itself.

    Reporting institutions, position values, and report periods from live
    Form 13F filings (served from the PortfolioFuture data CDN).

    Use when users ask:
    - "Who holds this fund institutionally?"
    - "Which firms own SPY?"
    """
    t = ticker.upper().strip()
    try:
        h = get_holders(t)
        out = _holders_summary(h, max_rows=max_rows)
        out["scope"] = "holders of the fund itself"
        return out
    except PortfolioFutureError as exc:
        return _error(t, "get_institutional_holders", exc)


@mcp.tool()
def get_opportunity_holders(ticker: str, top_n: int = 3) -> Dict[str, Any]:
    """Institutions holding the funds THIS fund can replace — the distribution view.

    For each opportunity target (incumbent funds this fund qualifies to
    displace) that publishes a 13F holder document, returns its SEC 13F
    institutional holders: the firms currently sitting on the replaceable
    assets. This is the sales-lead direction the web platform surfaces as
    "Who holds the funds it can replace?".

    Coverage note: 13F holder documents are published for ETFs; mutual-fund
    share classes are not on the data CDN and are listed under
    "without_13f_doc".

    Use when users ask:
    - "Who holds the funds it can replace?"
    - "Which institutions are we really competing for?"
    """
    t = ticker.upper().strip()
    try:
        # Look beyond top_n: some opportunity targets (mutual-fund share
        # classes) publish no 13F doc, so keep scanning until we fill top_n.
        peers = get_opportunity(t, top_n=max(top_n * 5, 20))
        targets: List[Dict[str, Any]] = []
        without_doc: List[str] = []
        for p in peers:
            if len(targets) >= top_n:
                break
            try:
                h = get_holders(p.ticker)
            except PortfolioFutureAPIError as exc:
                if getattr(exc, "status", None) == 404:
                    without_doc.append(p.ticker)  # no 13F doc published
                else:
                    targets.append({"replaced_fund": p.ticker, "error": str(exc)})
                continue
            except PortfolioFutureError as exc:
                targets.append({"replaced_fund": p.ticker, "error": str(exc)})
                continue
            targets.append({
                "replaced_fund": p.ticker,
                "fsi": p.fsi,
                "holder_firm_count": h.holder_firm_count,
                "total_value_usd": h.total_value_usd,
                "holders_url": get_fund_url(p.ticker, "holders"),
            })
        return {
            "target_ticker": t,
            "replaceable_funds_with_holders": len(targets),
            "replaceable_fund_holders": targets,
            "without_13f_doc": without_doc,
            "coverage_note": (
                "SEC 13F holder documents are published for ETFs; "
                "mutual-fund share classes are not on the data CDN."
            ),
            "opportunity_url": get_fund_url(t, "opportunity"),
        }
    except PortfolioFutureError as exc:
        return _error(t, "get_opportunity_holders", exc)


def main() -> None:
    """Entry point for the MCP server (stdio transport)."""
    mcp.run()


if __name__ == "__main__":
    main()
