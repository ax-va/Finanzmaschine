from finanzmaschine.core.lot_positions.base_lot_position import BaseLotPosition, R, IoOrder


class FifoLotPosition(BaseLotPosition):

    def close_record_fifo(self, record_out: R) -> None:
        return super().close_record(
            record_out=record_out,
            io_order=IoOrder.FIFO,
        )
