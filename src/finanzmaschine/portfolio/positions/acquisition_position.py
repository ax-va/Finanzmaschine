from abc import ABC
from typing import TypeVar, Generic

from finanzmaschine.portfolio.assets.asset import Asset
from finanzmaschine.portfolio.lots.acquisition_lot import AcquisitionLot
from finanzmaschine.portfolio.positions.priced_position import PricedPosition
from finanzmaschine.portfolio.records.non_trade_decrease_record import NonTradeDecreaseRecord
from finanzmaschine.portfolio.records.non_trade_increase_record import NonTradeIncreaseRecord
from finanzmaschine.portfolio.records.trade_record import TradeRecord

A = TypeVar("A", bound=Asset)
D = TypeVar("D", bound=NonTradeDecreaseRecord)
I = TypeVar("I", bound=NonTradeIncreaseRecord)
T = TypeVar("T", bound=TradeRecord)
L = TypeVar("L", bound=AcquisitionLot)


class AcquisitionPosition(PricedPosition[A, D, I | T, L], Generic[A, D, I, T, L], ABC):
    pass