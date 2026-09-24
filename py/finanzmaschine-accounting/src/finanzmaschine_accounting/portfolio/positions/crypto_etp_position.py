from finanzmaschine_accounting.portfolio.assets import CryptoEtp
from finanzmaschine_accounting.portfolio.lots import CryptoEtpLot
from finanzmaschine_accounting.portfolio.lots.priced_lot import RecordIn
from finanzmaschine_accounting.portfolio.positions.priced_position import PricedPosition


class CryptoEtpPosition(PricedPosition[CryptoEtp, CryptoEtpLot]):
    def _create_lot(self, record_in: RecordIn) -> CryptoEtpLot:
        return CryptoEtpLot(base_asset=self.base_asset, record_in=record_in)
