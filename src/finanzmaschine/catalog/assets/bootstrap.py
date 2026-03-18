from pathlib import Path

from finanzmaschine.catalog.asset_registry import asset_registry
from finanzmaschine.catalog.assets.asset_loader import load_assets

for etp in load_assets(Path(__file__).parent / "data"):
    asset_registry.register(etp)
