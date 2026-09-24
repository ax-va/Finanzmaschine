from finanzmaschine_accounting.portfolio.assets import Crypto
from finanzmaschine_accounting.portfolio.lots import CryptoLot
from finanzmaschine_accounting.portfolio.lots.priced_lot import RecordIn
from finanzmaschine_accounting.portfolio.positions.priced_position import PricedPosition


class CryptoPosition(PricedPosition[Crypto, CryptoLot]):
    def _create_lot(self, record_in: RecordIn) -> CryptoLot:
        return CryptoLot(base_asset=self.base_asset, record_in=record_in)

