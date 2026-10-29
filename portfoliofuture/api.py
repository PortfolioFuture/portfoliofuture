"""High-level, convenience functions over the PortfolioFuture client.

These use a module-level default client but accept an optional ``base_url``
for testing or pointing at a different deployment.
"""

from __future__ import annotations

from typing import List, Optional

from .client import DEFAULT_BASE_URL, PortfolioFutureClient
from .models import Decomposition, Peer, PeerCloud
from .exceptions import PortfolioFutureError

_default_client = PortfolioFutureClient()


def _client(base_url: Optional[str] = None) -> PortfolioFutureClient:
    return PortfolioFutureClient(base_url=base_url) if base_url else _default_client


def get_framework_info() -> dict:
    """Return metadata and the public API surface this client wraps."""
    return {
        "platform": "PortfolioFuture",
        "homepage": "https://portfoliofuture.com",
        "methodology": "SSRN Empirical Return Decomposition & Fund Substitution",
        "api_base": DEFAULT_BASE_URL,
        "endpoints": {
            "decomposition": "/api/fund-dna/<ticker>",
            "peers": "/api/fund-peers/<ticker>",
            "returns": "/api/etf/returns?tickers=<CSV>",
            "etf_profile": "/api/etf-profile/<ticker>",
            "etf_compare": "/api/etf-compare/<left>/<right>",
        },
        "note": "Every call performs a live HTTP request to the public API.",
    }


def get_decomposition(ticker: str, base_url: Optional[str] = None) -> Decomposition:
    """Fetch the Investable Return Decomposition for ``ticker``."""
    data = _client(base_url).decomposition(ticker)
    return Decomposition.from_dict(data)


def get_peers(ticker: str, base_url: Optional[str] = None) -> PeerCloud:
    """Fetch the full peer-substitution cloud for ``ticker``."""
    data = _client(base_url).peers(ticker)
    return PeerCloud.from_dict(data)


def get_returns(tickers, base_url: Optional[str] = None) -> dict:
    """Fetch period returns for one or more ETF tickers."""
    if isinstance(tickers, str):
        tickers = [tickers]
    return _client(base_url).returns(tickers)


def get_substitutes(
    ticker: str,
    top_n: int = 5,
    min_similarity: float = 0.0,
    cheaper_only: bool = False,
    base_url: Optional[str] = None,
) -> List[Peer]:
    """Return the closest fund substitutes for ``ticker``.

    Substitutes are ranked by descending similarity. Use ``min_similarity`` to
    require a minimum correlation and ``cheaper_only`` to keep only peers with
    a lower expense ratio than the target fund (when known).
    """
    cloud = get_peers(ticker, base_url=base_url)
    target_er = cloud.target_fund.get("expense_ratio")
    peers = [p for p in cloud.peers if p.ticker != ticker.upper()]
    if min_similarity > 0:
        peers = [p for p in peers if (p.similarity or 0) >= min_similarity]
    if cheaper_only and target_er is not None:
        peers = [p for p in peers if (p.expense_ratio or float("inf")) < target_er]
    peers.sort(key=lambda p: (p.similarity or 0), reverse=True)
    return peers[:top_n]


def get_fund_url(ticker: str, tool: str = "substitution") -> str:
    """Build a canonical PortfolioFuture web URL for a fund + tool."""
    ticker = ticker.lower().strip()
    tools = {
        "substitution": f"https://portfoliofuture.com/fund-opportunity/{ticker}",
        "decomposition": f"https://portfoliofuture.com/fund-decomposition/{ticker}",
        "compare": f"https://portfoliofuture.com/fund-compare/{ticker}",
        "holders": f"https://portfoliofuture.com/fund-holders/{ticker}",
    }
    return tools.get(tool, tools["substitution"])
