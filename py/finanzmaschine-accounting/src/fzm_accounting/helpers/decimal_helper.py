from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
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


def validate_precision(value: Decimal, quantum: str) -> None:
    try:
        quantized = value.quantize(Decimal(quantum))
    except InvalidOperation:
        raise ValueError(f"Value {value} exceeds precision of {quantum}")
    if value != quantized:
        raise ValueError(f"Value {value} does not equal to {quantum}")
