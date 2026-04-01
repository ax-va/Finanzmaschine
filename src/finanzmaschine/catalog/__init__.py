from pathlib import Path

from finanzmaschine.catalog.asset_loader import load_assets
from finanzmaschine.catalog.asset_registry import asset_registry
from finanzmaschine.portfolio.assets.crypto import Crypto
from finanzmaschine.portfolio.assets.crypto_etp import CryptoEtp
from finanzmaschine.portfolio.assets.currency import Currency

DIR_PATH = Path(__file__).parent


def register_assets():

    data_dir_path = DIR_PATH / "data"

    for asset in load_assets(data_dir_path / "currencies.yaml", asset_type=Currency):
        asset_registry.register(asset)

    for asset in load_assets(data_dir_path / "cryptos.yaml", asset_type=Crypto):
        asset_registry.register(asset)

    for asset in load_assets(data_dir_path / "crypto_etps.yaml", asset_type=CryptoEtp):
        asset_registry.register(asset)


register_assets()
