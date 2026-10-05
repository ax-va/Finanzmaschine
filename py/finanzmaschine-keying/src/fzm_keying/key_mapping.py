from typing import Protocol


class KeyMapping(Protocol):
    def get_key(self, value: str) -> str:
        ...

    def get_value(self, key: str) -> str:
        ...