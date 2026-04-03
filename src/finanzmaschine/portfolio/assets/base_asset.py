from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class BaseAsset[A: "BaseAsset"](ABC):
    id: str
    name: str

    def __eq__(self, other: A) -> bool:
        if type(self) != type(other):
            return False
        return self.id == other.id
