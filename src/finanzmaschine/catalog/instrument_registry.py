from collections import defaultdict
from typing import Dict, Tuple, List, DefaultDict

from finanzmaschine.catalog.asset_enum import Asset
from finanzmaschine.catalog.exchange_enum import Exchange
from finanzmaschine.core.market.instrument import Instrument

ExchangeTicker = Tuple[Exchange, str]


class InstrumentRegistry:

    def __init__(self):
        self._by_isin: Dict[str, Instrument] = {}
        self._by_exchange_ticker: Dict[ExchangeTicker, Instrument] = {}
        self._by_asset: DefaultDict[Asset, List[Instrument]] = defaultdict(list)
        self._by_wkn: Dict[str, Instrument] = {}

    def register(self, instrument: Instrument) -> None:

        if instrument.isin in self._by_isin:
            raise ValueError(f"Duplicate instrument {instrument.isin}")

        self._by_isin[instrument.isin] = instrument

        for exchange, ticker in instrument.tickers.items():
            self._by_exchange_ticker[(exchange, ticker)] = instrument

        asset = getattr(instrument, "asset", None)
        if asset is not None:
            self._by_asset[asset].append(instrument)

        wkn = self._extract_wkn(instrument)
        if wkn is not None:
            self._by_wkn[wkn] = instrument

    def get_by_isin(self, isin: str) -> Instrument:
        return self._by_isin.get(isin)

    def get_by_exchange_ticker(self, exchange: Exchange, ticker: str) -> Instrument:
        return self._by_exchange_ticker.get((exchange, ticker))

    def get_by_asset(self, asset: Asset) -> List[Instrument]:
        return self._by_asset.get(asset, [])

    def get_by_wkn(self, wkn: str) -> Instrument:
        return self._by_wkn.get(wkn)

    @staticmethod
    def _extract_wkn(instrument: Instrument):
        return instrument.country_data.get("DE", {}).get("WKN")
