from finanzmaschine.core.positions.base_position import BasePosition, R, IoOrder


class FifoPosition(BasePosition):

    def close_record_fifo(self, record_out: R) -> None:
        self.close_record(
            record_out=record_out,
            io_order=IoOrder.FIFO,
        )
