from abc import ABC
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BaseAsset(ABC):
    """Abstract base class for any asset"""

    id: str
    name: str
    precision: str

    def __eq__(self, other: Any) -> bool:
        if type(self) != type(other):
            return False
        return self.id == other.id
