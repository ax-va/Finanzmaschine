from pathlib import Path

from finanzmaschine.catalog.asset_loader import load_assets
from finanzmaschine.catalog.asset_registry import asset_registry
from finanzmaschine.portfolio.assets import Etp

for etp in load_assets(Path(__file__).parent / "data", asset_type=Etp):
    asset_registry.register(etp)
