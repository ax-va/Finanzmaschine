import httpx

from fzm_near.sync_clients.rpc_client import RpcClient
from fzm_near.sync_clients.txs_client import TxsClient


def fetch_final_block_height() -> int:
    """Fetches the height of the latest finalized NEAR block."""
    with httpx.Client(timeout=30) as http_client:
        rpc_client = RpcClient(http_client)
        return rpc_client.fetch_final_block_height()


def fetch_raw_txs(
    account_id: str,
    from_tx_block_height: int | None = None,
    up_to_tx_block_height: int | None = None,
) -> list[dict]:
    """Fetches raw account transactions within a block height range."""
    with httpx.Client(timeout=30) as http_client:
        txs_client = TxsClient(http_client)

        account_txs: list[dict] = txs_client.fetch_account_txs(
            account_id=account_id,
            from_tx_block_height=from_tx_block_height,
            up_to_tx_block_height=up_to_tx_block_height,
            is_success=True,
        )

        tx_hashes: list[str] = [
            tx["transaction_hash"]
            for tx in account_txs
        ]

        return txs_client.fetch_raw_txs(tx_hashes=tx_hashes)
