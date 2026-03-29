from typing import TypeVar, Generic, Tuple

from finanzmaschine.portfolio.assets import BaseAsset
from finanzmaschine.portfolio.lots.base_lot import BaseLot
from finanzmaschine.portfolio.records.non_sale_reduction_record import NonSaleReductionRecord
from finanzmaschine.portfolio.records.priced_record import PricedRecord

A = TypeVar('A' , bound=BaseAsset)
N = TypeVar("N", bound=NonSaleReductionRecord)
P = TypeVar("P", bound=PricedRecord)


class PricedLot(BaseLot, Generic[A, N, P]):

    def __init__(self, base_asset: A, record_in: P):
        super().__init__(base_asset, record_in)

    @property
    def records(self) -> Tuple[N | P, ...]:
        return super().records

    @property
    def record_in(self) -> P:
        return super().record_in

    @property
    def records_out(self) -> Tuple[N | P, ...]:
        return super().records_out

    @property
    def last_record(self) -> N | P:
        return super().last_record

    def close_record(self, record_out: N | P) -> N | P | None:
        return super().close_record(record_out)
