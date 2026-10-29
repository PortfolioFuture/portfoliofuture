"""Low-level HTTP client for the public PortfolioFuture API.

Uses only the Python standard library so the package installs with zero
third-party dependencies. Every method performs a live network call to
``https://portfoliofuture.com/api/*`` (or the ``base_url`` you configure).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

from .exceptions import PortfolioFutureAPIError, PortfolioFutureNetworkError

DEFAULT_BASE_URL = "https://portfoliofuture.com"
DEFAULT_USER_AGENT = "portfoliofuture-python/0.1.0"


class PortfolioFutureClient:
    """Thin HTTP wrapper around the PortfolioFuture public API."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 20.0,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.user_agent = user_agent

    def _get(self, path: str) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        request = urllib.request.Request(
            url,
            headers={"Accept": "application/json", "User-Agent": self.user_agent},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read()
                status = response.getcode()
        except urllib.error.HTTPError as exc:  # 4xx / 5xx
            raise PortfolioFutureAPIError(
                f"HTTP {exc.code} for {url}: {exc.reason}", status=exc.code, url=url
            ) from exc
        except Exception as exc:  # DNS / TLS / timeout / refused
            raise PortfolioFutureNetworkError(
                f"Network error contacting {url}: {exc}", url=url
            ) from exc

        if status != 200:
            raise PortfolioFutureAPIError(
                f"Unexpected status {status} for {url}", status=status, url=url
            )
        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise PortfolioFutureAPIError(
                f"Invalid JSON returned from {url}: {exc}", url=url
            ) from exc

    # --- endpoint helpers -------------------------------------------------

    def decomposition(self, ticker: str) -> dict:
        """Investable Return Decomposition for one fund."""
        return self._get(f"/api/fund-dna/{ticker}")

    def peers(self, ticker: str) -> dict:
        """Full peer-substitution cloud for one fund."""
        return self._get(f"/api/fund-peers/{ticker}")

    def returns(self, tickers) -> dict:
        """Period returns for one or more ETF tickers (comma-separated)."""
        if isinstance(tickers, str):
            tickers = [tickers]
        joined = ",".join(t.strip().upper() for t in tickers)
        return self._get(f"/api/etf/returns?tickers={urllib.parse.quote(joined)}")

    def etf_profile(self, ticker: str) -> dict:
        """Structured ETF profile."""
        return self._get(f"/api/etf-profile/{ticker}")

    def etf_compare(self, left: str, right: str) -> dict:
        """Head-to-head comparison of two funds."""
        return self._get(f"/api/etf-compare/{left}/{right}")
