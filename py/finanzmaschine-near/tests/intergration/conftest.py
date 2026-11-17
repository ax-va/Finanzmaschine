from fzm_keying.protocols import KeyMappingProtocol
from fzm_keying.storage.csv_key_mapping import CsvKeyMapping

import pytest


@pytest.fixture(scope="session")
def key_mapping() -> KeyMappingProtocol:
    return CsvKeyMapping(
        "/home/delorian/PycharmProjects/Finanzmaschine/py/finanzmaschine-near/key_mapping.csv"
    )


@pytest.fixture(scope="session")
def account_key() -> str:
    return "27a57234-2770-4a5e-b8a2-13ae9028d045"


@pytest.fixture(scope="session")
def tx_key() -> str:
    return "18efcc2e-378d-49b0-9229-855167eb2163"


@pytest.fixture(scope="session")
def account_id(
    account_key: str,
    key_mapping: KeyMappingProtocol,
) -> str:
    return key_mapping.get_value(account_key)


@pytest.fixture(scope="session")
def tx_hash(
    tx_key: str,
    key_mapping: KeyMappingProtocol,
) -> str:
    return key_mapping.get_value(tx_key)
