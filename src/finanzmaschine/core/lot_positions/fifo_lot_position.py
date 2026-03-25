from typing import override

from finanzmaschine.core.lot_positions.base_lot_position import BaseLotPosition, R, Out


class FifoLotPosition(BaseLotPosition):

    def fifo_close_record(self, record_out: R) -> None:
        return super().close_record(
            record_out=record_out,
            out=Out.FI,
        )
