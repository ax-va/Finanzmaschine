from pathlib import Path

from finanzmaschine.catalog import registry
from finanzmaschine.catalog.etps.etp_loader import load_etps

for etp in load_etps(Path(__file__).parent / "data"):
    registry.register(etp)
