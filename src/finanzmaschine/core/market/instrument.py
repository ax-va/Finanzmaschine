from dataclasses import dataclass, field
from typing import Dict

from finanzmaschine.catalog.exchange import Exchange


@dataclass(frozen=True)
class Instrument:
    isin: str
    name: str
    country_data: Dict[str, Dict[str, str]] = field(default_factory=dict)
    tickers: Dict[Exchange, str] = field(default_factory=dict)