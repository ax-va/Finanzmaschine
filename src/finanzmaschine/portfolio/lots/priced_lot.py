from typing import TypeVar

from finanzmaschine.portfolio.assets import BaseAsset
from finanzmaschine.portfolio.lots.base_lot import BaseLot
from finanzmaschine.portfolio.records.non_sale_reduction_record import NonSaleReductionRecord
from finanzmaschine.portfolio.records.priced_record import PricedRecord

A = TypeVar('A' , bound=BaseAsset)
N = TypeVar("N", bound=NonSaleReductionRecord)
P = TypeVar("P", bound=PricedRecord)


class PricedLot(BaseLot[A, N | P, P]):

    @property
    def initial_cost_basis(self) -> float:
        # workaround for typechecker
        record_in: PricedRecord = self.record_in
        return record_in.gross_value + record_in.fee

    @property
    def unit_cost_basis(self) -> float:
        # workaround for typechecker
        record_in: PricedRecord = self.record_in
        return self.initial_cost_basis / record_in.quantity

    @property
    def open_cost_basis(self) -> float:
        return self.quantity_open * self.unit_cost_basis
