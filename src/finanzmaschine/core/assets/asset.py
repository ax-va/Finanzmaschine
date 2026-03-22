from dataclasses import dataclass
from typing import TypeVar

A = TypeVar("A", bound="Asset")


@dataclass(frozen=True)
class Asset:
    id: str
    name: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Asset):
            return NotImplemented

        return self.id == other.id
