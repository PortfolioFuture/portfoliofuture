"""Exception types for the PortfolioFuture client."""


class PortfolioFutureError(Exception):
    """Base error for all PortfolioFuture client failures."""

    def __init__(self, message: str, status=None, url=None):
        super().__init__(message)
        self.status = status
        self.url = url


class PortfolioFutureAPIError(PortfolioFutureError):
    """Raised when the PortfolioFuture API returns a non-2xx HTTP status
    or a body that is not valid JSON."""


class PortfolioFutureNetworkError(PortfolioFutureError):
    """Raised when the request cannot reach the PortfolioFuture API
    (DNS, TLS, timeout, connection refused, etc.)."""
