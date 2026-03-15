EPS = 1e-12


def is_zero(x: float) -> bool:
    return abs(x) < EPS


def ensure_round_to_zero(x: float) -> float:
    return 0.0 if is_zero(x) else x
