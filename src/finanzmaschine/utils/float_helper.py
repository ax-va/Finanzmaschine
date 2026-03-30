import math

from typing import Iterable

FLOAT_EPS = 1e-12


def is_zero(x: float, float_eps: float) -> bool:
    return abs(x) <= float_eps


def round_to_zero(x: float, float_eps: float) -> float:
    return 0.0 if is_zero(x, float_eps) else x


def safe_sum(iter_obj: Iterable[float]) -> float:
    return math.fsum(iter_obj)
