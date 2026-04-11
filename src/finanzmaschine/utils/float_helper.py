import math

from typing import Iterable

FLOAT_EPS = 1e-12


def is_zero(value: float, eps: float) -> bool:
    return abs(value) < eps


def round_to_zero(value: float, eps: float = FLOAT_EPS) -> float:
    return 0.0 if is_zero(value, eps) else value


def safe_sum(values: Iterable[float]) -> float:
    return math.fsum(values)
