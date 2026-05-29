from pathlib import Path

from finanzmaschine_core.catalog.asset_loader import load_assets
from finanzmaschine_core.catalog.asset_registry import asset_registry
from finanzmaschine_core.portfolio.assets.crypto import Crypto
from finanzmaschine_core.portfolio.assets.crypto_etp import CryptoEtp
from finanzmaschine_core.portfolio.assets.currency import Currency
from finanzmaschine_core.portfolio.assets.liquid_staking_token import LiquidStakingToken

DIR_PATH = Path(__file__).parent


def register_assets():

    data_dir_path = DIR_PATH / "data"

    for asset in load_assets(data_dir_path / "currencies.yaml", asset_type=Currency):
        asset_registry.register(asset)

    for asset in load_assets(data_dir_path / "cryptos.yaml", asset_type=Crypto):
        asset_registry.register(asset)

    for asset in load_assets(data_dir_path / "liquid_staking_tokens.yaml", asset_type=LiquidStakingToken):
        asset_registry.register(asset)

    for asset in load_assets(data_dir_path / "crypto_etps.yaml", asset_type=CryptoEtp):
        asset_registry.register(asset)


register_assets()
