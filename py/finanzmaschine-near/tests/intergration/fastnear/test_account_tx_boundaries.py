import httpx
import pytest

from fzm_near.sync_clients.fastnear_tx_client import FastNearTxClient

block_height = 224848800


def fetch_hashes(
    payload: dict,
    tx_client: FastNearTxClient,
) -> set[str]:
    data = tx_client.post(
        url=tx_client.TX_MAIN_URL + "/v0/account",
        payload=payload,
        error_name="FastNEAR Tx error",
    )

    return {
        tx["transaction_hash"]
        for tx in data["account_txs"]
    }


@pytest.mark.parametrize(
    "from_tx_block_height_inclusive, "
    "to_tx_block_height_inclusive, "
    "expected",
    [
        (block_height, block_height, True),
        (block_height - 1, block_height, True),
        (block_height, block_height + 1, True),
        (block_height - 2, block_height - 1, False),
        (block_height + 1, block_height + 2, False),
    ]
)
def test_account_tx_block_height_boundaries(
    from_tx_block_height_inclusive: int,
    to_tx_block_height_inclusive: int,
    expected: bool,
    account_id: str,
    tx_hash: str,
):
    """
    Verifies that both block height boundaries
    of the FastNEAR `/v0/account` endpoint are inclusive.

    Checks that a known transaction is returned
    when its block height falls within the specified range,
    including either boundary, and excluded when it falls outside the range.

    This integration test detects changes in the API's boundary behavior.
    """

    with httpx.Client(timeout=30) as http_client:
        tx_client = FastNearTxClient(http_client)

        payload = {
            "account_id": account_id,
            "is_signer": True,
            "limit": 200,
            "from_tx_block_height": from_tx_block_height_inclusive,
            "to_tx_block_height": to_tx_block_height_inclusive,
        }

        actual = tx_hash in fetch_hashes(
            payload=payload,
            tx_client=tx_client,
        )

        assert actual is expected, (
            f"Unexpected transaction range behavior: "
            f"from={from_tx_block_height_inclusive}, "
            f"to={to_tx_block_height_inclusive}, "
            f"expected={expected}, actual={actual}"
        )
