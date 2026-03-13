from typing import Dict

from finanzmaschine.core.market.instrument import Instrument


class InstrumentRegistry:

    def __init__(self):
        self._by_isin: Dict[str, Instrument] = {}
        self._by_ticker: Dict[str, Instrument] = {}
        self._by_wkn: Dict[str, Instrument] = {}

    def register(self, instrument: Instrument) -> None:
        self._by_isin[instrument.isin] = instrument

        for ticker in instrument.tickers.values():
            self._by_ticker[ticker] = instrument

        wkn = instrument.country_data.get("DE", {}).get("WKN")
        if wkn is not None:
            self._by_wkn[wkn] = instrument

    def by_isin(self, isin: str) -> Instrument:
        return self._by_isin[isin]

    def by_ticker(self, ticker: str) -> Instrument:
        return self._by_ticker[ticker]

    def by_wkn(self, wkn: str) -> Instrument:
        return self._by_wkn[wkn]