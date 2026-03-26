from finanzmaschine.core.positions.base_position import BasePosition, R, IoOrder


class LifoPosition(BasePosition):

    def close_record_lifo(self, record_out: R) -> None:
        self.close_record(
            record_out=record_out,
            io_order=IoOrder.LIFO,
        )
