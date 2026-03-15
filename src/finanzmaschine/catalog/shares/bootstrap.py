from pathlib import Path

from finanzmaschine.catalog import registry
from finanzmaschine.catalog.shares.loader import load_shares

for share in load_shares(Path(__file__).parent / "data"):
    registry.register(share)
