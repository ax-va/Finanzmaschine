from dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    id: str
    name: str
