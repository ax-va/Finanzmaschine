from abc import ABC
from typing import TypeVar, Generic

from finanzmaschine.portfolio.assets import BaseAsset
from finanzmaschine.portfolio.lots.base_lot import BaseLot
from finanzmaschine.portfolio.records.non_trade_decrease_record import NonTradeDecreaseRecord
from finanzmaschine.portfolio.records.priced_record import PricedRecord
from finanzmaschine.utils.float_helper import safe_sum

A = TypeVar('A', bound=BaseAsset)
D = TypeVar("D", bound=NonTradeDecreaseRecord)
P = TypeVar("P", bound=PricedRecord)


class PricedLot(BaseLot[A, D | P, P], Generic[A, D, P], ABC):

    @property
    def quantity_realized(self) -> float:
        return safe_sum(r_out.quantity for r_out in self.records_out if isinstance(r_out, PricedRecord))

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
    def realized_cost_basis(self) -> float:
        return self.quantity_realized * self.unit_cost_basis
