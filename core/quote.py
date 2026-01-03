import datetime


class Quote:
    def __init__(self) -> None:
        self.data = {
            "GB00BLD4ZM24": {
                "2026-01-02 16:15": {
                    "ETP": {
                        "bid_eur": None,
                        "ask_eur": None,
                    },
                    "ETH": {
                        "bid_eur": 2610,
                        "ask_eur": 2613,
                        "local_high_eur": 4000,
                    }
                }
            }
        }
