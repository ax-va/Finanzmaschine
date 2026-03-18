from pathlib import Path

from finanzmaschine.catalog.asset_registry import asset_registry
from finanzmaschine.catalog.etps.etp_loader import load_etps

for etp in load_etps(Path(__file__).parent / "data"):
    asset_registry.register(etp)
