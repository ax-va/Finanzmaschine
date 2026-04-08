from typing import Dict, List

from finanzmaschine.portfolio.assets.asset import Asset


class AssetRegistry[A: Asset]:
    def __init__(self):
        self._by_id: Dict[str, A] = {}

    def register(self, asset: A) -> A:
        if asset.id in self._by_id:
            raise ValueError(f"Duplicate asset {asset.id!r}")
        self._by_id[asset.id] = asset
        return asset

    def get_all(self) -> List[A]:
        return list(self._by_id.values())

    def get(self, key: str) -> A:
        return self._by_id.get(key)


asset_registry = AssetRegistry()
