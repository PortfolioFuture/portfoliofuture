"""Typed result models parsed from the PortfolioFuture API responses.

All models are built defensively with ``.get()`` so the client keeps working
even if the upstream API adds or renames fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Decomposition:
    """Investable Return Decomposition for a single fund.

    The ``raw`` attribute always holds the full JSON response for any field
    not surfaced as a first-class attribute.
    """

    ticker: str = ""
    fund_name: str = ""
    as_of: Optional[str] = None
    window_years: Optional[int] = None
    n_common_weeks: Optional[int] = None
    method: Optional[str] = None
    algorithm_version: Optional[str] = None
    weights: Dict[str, float] = field(default_factory=dict)
    basket: List[dict] = field(default_factory=list)
    block_analytics: List[dict] = field(default_factory=list)
    r2: Optional[float] = None
    r2_full: Optional[float] = None
    tracking_error_ann: Optional[float] = None
    information_ratio: Optional[float] = None
    residual_ir_annualized: Optional[float] = None
    residual_alpha_ann: Optional[float] = None
    residual_vol_ann: Optional[float] = None
    residual_pir: Optional[float] = None
    fee_saving_bps: Optional[float] = None
    target_fee_bps: Optional[float] = None
    replica_fee_bps: Optional[float] = None
    expense_ratio: Optional[float] = None
    aum: Optional[float] = None
    universe_size: Optional[int] = None
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "Decomposition":
        return cls(
            ticker=d.get("ticker", ""),
            fund_name=d.get("fund_name", ""),
            as_of=d.get("as_of"),
            window_years=d.get("window_years"),
            n_common_weeks=d.get("n_common_weeks"),
            method=d.get("method"),
            algorithm_version=d.get("algorithm_version"),
            weights=d.get("weights") or {},
            basket=d.get("basket") or [],
            block_analytics=d.get("block_analytics") or [],
            r2=d.get("r2"),
            r2_full=d.get("r2_full"),
            tracking_error_ann=d.get("tracking_error_ann"),
            information_ratio=d.get("information_ratio"),
            residual_ir_annualized=d.get("residual_ir_annualized"),
            residual_alpha_ann=d.get("residual_alpha_ann"),
            residual_vol_ann=d.get("residual_vol_ann"),
            residual_pir=d.get("residual_pir"),
            fee_saving_bps=d.get("fee_saving_bps"),
            target_fee_bps=d.get("target_fee_bps"),
            replica_fee_bps=d.get("replica_fee_bps"),
            expense_ratio=d.get("expense_ratio"),
            aum=d.get("aum"),
            universe_size=d.get("universe_size"),
            raw=d,
        )


@dataclass
class Peer:
    """A single fund in a peer-substitution cloud."""

    ticker: str = ""
    name: str = ""
    is_mutual_fund: bool = False
    similarity: Optional[float] = None
    pir: Optional[float] = None
    tracking_error: Optional[float] = None
    expense_ratio: Optional[float] = None
    aum: Optional[float] = None
    volume: Optional[float] = None
    dividend_yield: Optional[float] = None
    return_3m: Optional[float] = None
    return_6m: Optional[float] = None
    return_1y: Optional[float] = None
    return_3y: Optional[float] = None
    return_5y: Optional[float] = None
    active_return_ann: Optional[float] = None
    lower_limit_95: Optional[float] = None
    upper_limit_95: Optional[float] = None
    win_rate: Optional[float] = None
    win_average: Optional[float] = None
    shared_weeks: Optional[int] = None


@dataclass
class PeerCloud:
    """Full peer-substitution cloud for a target fund.

    The upstream response encodes each metric as a parallel list; we zip
    them into a list of :class:`Peer` objects for convenient access.
    """

    target: str = ""
    count: int = 0
    contract: Optional[str] = None
    release: Optional[str] = None
    target_fund: dict = field(default_factory=dict)
    peers: List[Peer] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "PeerCloud":
        tickers: List[str] = d.get("tickers") or []
        cols = {key: (d.get(key) or []) for key in (
            "names", "is_mutual_fund", "similarity", "pir", "tracking_error",
            "expense_ratio", "aum", "volume", "dividend_yield",
            "return_3m", "return_6m", "return_1y", "return_3y", "return_5y",
            "active_return_ann", "lower_limit_95", "upper_limit_95",
            "win_rate", "win_average", "shared_weeks",
        )}

        def pick(key: str, i: int):
            seq = cols[key]
            return seq[i] if i < len(seq) else None

        peers: List[Peer] = []
        for i, ticker in enumerate(tickers):
            sw = pick("shared_weeks", i)
            peers.append(Peer(
                ticker=ticker,
                name=pick("names", i) or "",
                is_mutual_fund=bool(pick("is_mutual_fund", i)),
                similarity=pick("similarity", i),
                pir=pick("pir", i),
                tracking_error=pick("tracking_error", i),
                expense_ratio=pick("expense_ratio", i),
                aum=pick("aum", i),
                volume=pick("volume", i),
                dividend_yield=pick("dividend_yield", i),
                return_3m=pick("return_3m", i),
                return_6m=pick("return_6m", i),
                return_1y=pick("return_1y", i),
                return_3y=pick("return_3y", i),
                return_5y=pick("return_5y", i),
                active_return_ann=pick("active_return_ann", i),
                lower_limit_95=pick("lower_limit_95", i),
                upper_limit_95=pick("upper_limit_95", i),
                win_rate=pick("win_rate", i),
                win_average=pick("win_average", i),
                shared_weeks=int(sw) if sw is not None else None,
            ))
        return cls(
            target=d.get("target", ""),
            count=d.get("count", len(peers)),
            contract=d.get("contract"),
            release=d.get("release"),
            target_fund=d.get("target_fund") or {},
            peers=peers,
        )
