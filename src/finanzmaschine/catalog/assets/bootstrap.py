from pathlib import Path

from finanzmaschine.catalog.asset_loader import load_assets
from finanzmaschine.catalog.asset_registry import asset_registry

for asset in load_assets(Path(__file__).parent / "data"):
    asset_registry.register(asset)
