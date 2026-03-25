from finanzmaschine.core.lot_positions.base_lot_position import BaseLotPosition, R


class FifoLotPosition(BaseLotPosition):

    def close_record(self, record_out: R) -> None:
        return super()._close_record_fifo(record_out=record_out)
