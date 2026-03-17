from typing import Dict, List

from finanzmaschine.core.market.security import Security


class SecurityRegistry:
    def __init__(self):
        self._by_isin: Dict[str, Security] = {}

    def register(self, security: Security) -> Security:
        if security.isin in self._by_isin:
            raise ValueError(f"Duplicate security {security.isin}")

        self._by_isin[security.isin] = security

        return security

    def get_all(self) -> List[Security]:
        return list(self._by_isin.values())

    def get_by_isin(self, isin: str) -> Security:
        return self._by_isin.get(isin)


registry = SecurityRegistry()
