from dataclasses import dataclass


@dataclass(frozen=True)
class BaseAsset[A: "BaseAsset"]:
    id: str
    name: str

    def __eq__(self, other: A) -> bool:
        return self.id == other.id
