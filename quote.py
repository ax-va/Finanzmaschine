import datetime


class Quote:
    def __init__(self) -> None:
        self.data = {
            "GB00BLD4ZM24": {
                datetime.datetime(year=2026, month=1, day=2, hour=16, minute=15): {
                    "bid_etp_eur": None,
                    "ask_etp_eur": None,
                    "bid_eth_eur": 2610,
                    "ask_eth_eur": 2613,
                    "eth_local_high": 4000,
                }
            }
        }
