from dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    name: str