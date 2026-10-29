"""PortfolioFuture — Python client for the public PortfolioFuture quant API.

Every function performs a live HTTP call to ``https://portfoliofuture.com/api/*``
and returns parsed, typed results. No data is bundled or fabricated.
"""

from .client import DEFAULT_BASE_URL, PortfolioFutureClient
from .models import Decomposition, Peer, PeerCloud
from .exceptions import (
    PortfolioFutureError,
    PortfolioFutureAPIError,
    PortfolioFutureNetworkError,
)
from .api import (
    get_framework_info,
    get_decomposition,
    get_peers,
    get_returns,
    get_substitutes,
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
    "PortfolioFutureError",
    "PortfolioFutureAPIError",
    "PortfolioFutureNetworkError",
    "get_framework_info",
    "get_decomposition",
    "get_peers",
    "get_returns",
    "get_substitutes",
    "get_fund_url",
]
