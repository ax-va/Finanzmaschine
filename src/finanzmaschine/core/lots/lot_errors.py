class LotError(Exception):
    pass


class ClosingMoreThanOpenQuantityError(LotError):
    def __init__(self) -> None:
        super().__init__("Cannot close more than open quantity")


class OrderingByDatetimeError(LotError):
    def __init__(self) -> None:
        super().__init__("Records must be ordered by datetime")