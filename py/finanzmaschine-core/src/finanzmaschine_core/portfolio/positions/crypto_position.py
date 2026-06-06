from finanzmaschine_core.portfolio.assets import Crypto
from finanzmaschine_core.portfolio.lots import CryptoLot
from finanzmaschine_core.portfolio.lots.priced_lot import RecordIn
from finanzmaschine_core.portfolio.positions.priced_position import PricedPosition


class CryptoPosition(PricedPosition[Crypto, CryptoLot]):
    def _create_lot(self, record_in: RecordIn) -> CryptoLot:
        return CryptoLot(base_asset=self.base_asset, record_in=record_in)

