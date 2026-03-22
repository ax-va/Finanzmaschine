from dataclasses import dataclass
from typing import TypeVar

A = TypeVar("A", bound="Asset")


@dataclass(frozen=True)
class Asset:
    id: str
    name: str
