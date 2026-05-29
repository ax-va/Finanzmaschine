from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable


def round_to_quantum(value: Decimal, quantum: str) -> Decimal:
    return value.quantize(Decimal(quantum), rounding=ROUND_HALF_UP).normalize()


def round_to_cents(value: Decimal) -> Decimal:
    return round_to_quantum(value, "0.01")


def safe_sum(values: Iterable[Decimal]) -> Decimal:
    return sum(values, Decimal("0"))


def is_zero(value: Decimal, quantum: str) -> bool:
    return abs(value) < Decimal(quantum)


def round_to_zero(value: Decimal, quantum: str) -> Decimal:
    return Decimal("0") if is_zero(value, quantum) else value
