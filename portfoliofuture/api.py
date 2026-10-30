"""High-level, convenience functions over the PortfolioFuture client.

These use a module-level default client but accept an optional ``base_url``
for testing or pointing at a different deployment.

Product framing note
---------------------
The public verbs are **opportunity** and **evaluate opportunity**, never
"substitution". ``get_opportunity`` answers "which funds can *this* fund
replace?" (the challenger's upside), and ``evaluate_opportunity`` answers
"are these two funds comparable, and which is better?" — both built on the
live peer-cloud and head-to-head endpoints. The underlying research is the
published fund-substitution / return-decomposition methodology; the surface
language is opportunity because that is what an allocator acts on.
"""

from __future__ import annotations

from typing import List, Optional

from .client import DEFAULT_BASE_URL, PortfolioFutureClient
from .models import Comparison, Decomposition, Holders, Peer, PeerCloud
from .exceptions import PortfolioFutureError

_default_client = PortfolioFutureClient()


def _client(base_url: Optional[str] = None) -> PortfolioFutureClient:
    return PortfolioFutureClient(base_url=base_url) if base_url else _default_client


def get_framework_info() -> dict:
    """Return metadata and the public API surface this client wraps."""
    return {
        "platform": "PortfolioFuture",
        "homepage": "https://portfoliofuture.com",
        "methodology": "SSRN Empirical Return Decomposition & Fund Opportunity",
        "api_base": DEFAULT_BASE_URL,
        "endpoints": {
            "decomposition": "/api/fund-dna/<ticker>",
            "peers": "/api/fund-peers/<ticker>",
            "opportunity": "/api/fund-peers/<ticker> (ranked for opportunity)",
            "compare": "/api/etf-compare/<left>/<right>",
            "returns": "/api/etf/returns?tickers=<CSV>",
            "etf_profile": "/api/etf-profile/<ticker>",
            "holders": "data.portfoliofuture.com/tickers/ticker-<hex>.json (CDN)",
        },
        "note": "Every call performs a live HTTP request to the public API.",
    }


def get_decomposition(ticker: str, base_url: Optional[str] = None) -> Decomposition:
    """Fetch the Investable Return Decomposition for ``ticker``."""
    data = _client(base_url).decomposition(ticker)
    return Decomposition.from_dict(data)


def get_peers(ticker: str, base_url: Optional[str] = None) -> PeerCloud:
    """Fetch the full empirical peer cloud for ``ticker``.

    The peer cloud is the raw similarity graph: every fund with a non-trivial
    weekly-return correlation to ``ticker``, with similarity, PIR, tracking
    error, expense ratio, and historical returns. Use :func:`get_opportunity`
    for the ranked, action-oriented view.
    """
    data = _client(base_url).peers(ticker)
    return PeerCloud.from_dict(data)


def get_opportunity(
    ticker: str,
    top_n: int = 5,
    min_fsi: float = 0.0,
    min_similarity: float = 0.0,
    cheaper_only: bool = False,
    base_url: Optional[str] = None,
) -> List[Peer]:
    """Return the funds that *this* fund can replace — its opportunity.

    Framing is the challenger's upside: you hold or research ``ticker``, and the
    result tells you which incumbent funds it qualifies to displace.

    Qualification is **FSI (Fund Substitution Index)** — return similarity ×
    consistent outperformance of the target over the peer (P(IR>0)). The API's
    raw ``pir`` is the peer's P(IR>0) **against** the target; ``1 − pir`` is the
    target's own edge, so ``fsi = similarity × target_conviction``. Each
    :class:`Peer` exposes ``similarity``, ``pir`` (raw), ``target_conviction =
    1 - pir``, and ``fsi`` — this call ranks by ``fsi``. The web platform
    qualifies replacements at FSI > 80 (its 0-100 display), i.e.
    ``min_fsi=0.80`` here.

    Args:
        ticker: The fund you are evaluating as the challenger.
        top_n: How many opportunity targets to return.
        min_fsi: Qualification line — drop peers below this FSI (0-1).
        min_similarity: Additionally require this return similarity (0-1).
        cheaper_only: Optionally keep only peers whose expense ratio is higher
            than the target's (a cost tie-break, not the thesis).

    Returns:
        A list of :class:`Peer` ranked by descending FSI — the strongest
        replacement (most similar AND most reliably beaten) first.
    """
    cloud = get_peers(ticker, base_url=base_url)
    target_er = cloud.target_fund.get("expense_ratio")
    peers = [p for p in cloud.peers if p.ticker != ticker.upper()]
    if min_fsi > 0:
        peers = [p for p in peers if (p.fsi or 0) >= min_fsi]
    if min_similarity > 0:
        peers = [p for p in peers if (p.similarity or 0) >= min_similarity]
    if cheaper_only and target_er is not None:
        peers = [
            p for p in peers
            if (p.expense_ratio is not None and target_er < p.expense_ratio)
        ]
    peers.sort(key=lambda p: (p.fsi or 0), reverse=True)
    return peers[:top_n]


def evaluate_opportunity(
    left: str,
    right: str,
    base_url: Optional[str] = None,
) -> Comparison:
    """Evaluate whether two funds are comparable and which is better.

    Calls the live head-to-head endpoint and returns a :class:`Comparison`
    with the empirical similarity, a ``comparable`` flag, and — when the two
    funds move together — a ``better_ticker`` picked on **FSI** (Fund
    Substitution Index — return similarity × consistent outperformance): the
    higher FSI ranks as better. Both directions are scored (``fsi_left``,
    ``fsi_right``).

    Args:
        left: Ticker of the fund you hold or are comparing from.
        right: Ticker of the fund you are comparing against.

    Returns:
        A :class:`Comparison` (similarity, correlation, PIR, FSI both ways,
        comparable flag, and the higher-FSI ticker when comparable).
    """
    data = _client(base_url).etf_compare(left, right)
    return Comparison.from_dict(data)


def get_returns(tickers, base_url: Optional[str] = None) -> dict:
    """Fetch period returns for one or more ETF tickers."""
    if isinstance(tickers, str):
        tickers = [tickers]
    return _client(base_url).returns(tickers)


def get_holders(ticker: str, base_url: Optional[str] = None) -> Holders:
    """Fetch institutional 13F ownership for ``ticker`` from the data CDN.

    Returns a :class:`Holders` with the reporting institution count, total
    position value, and the per-institution ``rows`` (firm key, position value,
    share count, report period, and more). This is the same institutional
    ownership directory surfaced on the web platform at ``/fund-holders``.
    """
    data = _client(base_url).holders(ticker)
    return Holders.from_dict(data)


def get_fund_url(ticker: str, tool: str = "opportunity") -> str:
    """Build a canonical PortfolioFuture web URL for a fund + tool."""
    ticker = ticker.lower().strip()
    tools = {
        "opportunity": f"https://portfoliofuture.com/fund-opportunity/{ticker}",
        "decomposition": f"https://portfoliofuture.com/fund-decomposition/{ticker}",
        "compare": f"https://portfoliofuture.com/fund-compare/{ticker}",
        "holders": f"https://portfoliofuture.com/fund-holders/{ticker}",
    }
    return tools.get(tool, tools["opportunity"])
