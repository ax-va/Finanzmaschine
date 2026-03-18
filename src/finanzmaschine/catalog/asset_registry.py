from typing import Dict, List

from finanzmaschine.core.assets.asset import Asset


class AssetRegistry:
    def __init__(self):
        self._by_id: Dict[str, Asset] = {}

    def register(self, asset: Asset) -> Asset:
        if asset.id in self._by_id:
            raise ValueError(f"Duplicate asset {asset.id!r}")

        self._by_id[asset.id] = asset

        return asset

    def get_all(self) -> List[Asset]:
        return list(self._by_id.values())

    def get(self, key: str) -> Asset:
        return self._by_id.get(key)


asset_registry = AssetRegistry()
