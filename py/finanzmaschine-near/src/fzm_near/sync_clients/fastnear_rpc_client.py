import base64
import json
import logging
from typing import Any

from fzm_near.sync_clients.http_client import HttpClient

logger = logging.getLogger(__name__)


class FastNearRpcClient(HttpClient):
    _RPC_MAINNET_URL = "https://rpc.mainnet.fastnear.com"
    _ARCHIVAL_RPC_MAINNET_URL = "https://archival-rpc.mainnet.fastnear.com"

    def call_view_function(
        self,
        contract_id: str,
        method_name: str,
        args: dict,
        block_height: int,
    ) -> bytes:
        """
        Calls a NEAR smart contract view function at a given block height.
        The call is read-only and does not create a transaction or modify blockchain state.

        Args:
            contract_id: NEAR account ID of the smart contract.
            method_name: Name of the view function to call.
            args: Arguments passed to the contract function.
            block_height: Block height at which to query the contract state.

        Returns:
            Raw bytes returned by the view function.
        """
        args_base64 = base64.b64encode(
            json.dumps(args).encode()
        ).decode()

        payload = {
            "jsonrpc": "2.0",
            "id": "staking",
            "method": "query",
            "params": {
                "request_type": "call_function",
                "account_id": contract_id,
                "method_name": method_name,
                "args_base64": args_base64,
                "block_id": block_height,
                }
        }

        data = self._post(
            url=self._ARCHIVAL_RPC_MAINNET_URL,
            payload=payload,
            error_name="FastNEAR RPC error",
        )

        result = data["result"]["result"]

        return bytes(result)

    def fetch_final_block_height(self) -> int:
        block = self._fetch_block(
            url=self._RPC_MAINNET_URL,
            params={
                "finality": "final",
            }
        )

        return block["header"]["height"]

    def fetch_block_timestamp_nanoseconds(
        self,
        block_height: int,
    ) -> int:
        block = self._fetch_block(
            url=self._ARCHIVAL_RPC_MAINNET_URL,
            params={
                "block_id": block_height,
            }
        )

        return int(block["header"]["timestamp_nanosec"])

    def is_staking_pool_whitelisted(
        self,
        pool_id: str,
        block_height: int,
    ) -> bool:
        """
        Check whether a staking pool is whitelisted at a given block height.

        Args:
            pool_id: Staking pool ID.
            block_height: Block height at which to query the pool state.

        Returns:
            `True` if staking pool is whitelisted, `False` otherwise.
        """

        result = self.call_view_function(
            contract_id="lockup-whitelist.near",
            method_name="is_whitelisted",
            args={"staking_pool_account_id": pool_id},
            block_height=block_height,
        )

        value = json.loads(result)

        if not isinstance(value, bool):
            raise ValueError(
                f"Unexpected whitelist response for {pool_id}: {value!r}"
            )

        return value

    def _fetch_block(
        self,
        url: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": "staking",
            "method": "block",
            "params": params,
        }

        data = self._post(
            url=url,
            payload=payload,
            error_name="FastNEAR RPC error",
        )

        return data["result"]
