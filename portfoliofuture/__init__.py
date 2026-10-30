"""PortfolioFuture — Python client for the public PortfolioFuture quant API.

Every function performs a live HTTP call to ``https://portfoliofuture.com/api/*``
and returns parsed, typed results. No data is bundled or fabricated.

Lead verbs are **opportunity** and **evaluate opportunity**: find which funds a
given fund can replace, and check whether two funds are comparable and which is
better. ``get_fund_substitution`` is the deliberate reverse view (which funds
can replace a given one).
"""

from .client import DEFAULT_BASE_URL, PortfolioFutureClient
from .models import Comparison, Decomposition, Holders, Peer, PeerCloud
from .exceptions import (
    PortfolioFutureError,
    PortfolioFutureAPIError,
    PortfolioFutureNetworkError,
)
from .api import (
    get_framework_info,
    get_decomposition,
    get_peers,
    get_opportunity,
    get_fund_substitution,
    evaluate_opportunity,
    get_returns,
    get_holders,
    get_fund_url,
)

__version__ = "0.1.0"
__author__ = "Vince (Qijun) Chen, CFA"

__all__ = [
    "PortfolioFutureClient",
    "DEFAULT_BASE_URL",
    "Decomposition",
    "PeerCloud",
    "Peer",
    "Comparison",
    "Holders",
    "PortfolioFutureError",
    "PortfolioFutureAPIError",
    "PortfolioFutureNetworkError",
    "get_framework_info",
    "get_decomposition",
    "get_peers",
    "get_opportunity",
    "get_fund_substitution",
    "evaluate_opportunity",
    "get_returns",
    "get_holders",
    "get_fund_url",
]
