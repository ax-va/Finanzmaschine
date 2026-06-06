from finanzmaschine_core.portfolio.assets import CryptoEtp
from finanzmaschine_core.portfolio.lots import CryptoEtpLot
from finanzmaschine_core.portfolio.lots.priced_lot import RecordIn
from finanzmaschine_core.portfolio.positions.priced_position import PricedPosition


class CryptoEtpPosition(PricedPosition[CryptoEtp, CryptoEtpLot]):
    def _create_lot(self, record_in: RecordIn) -> CryptoEtpLot:
        return CryptoEtpLot(base_asset=self.base_asset, record_in=record_in)
