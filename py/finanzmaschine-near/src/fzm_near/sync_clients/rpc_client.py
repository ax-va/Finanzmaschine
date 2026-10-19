import base64
import functools
import json
import logging

import httpx

from fzm_near.sync_clients.decorators import retry, rate_limit
from fzm_near.sync_clients.errors import BlockHeightNotFoundError

MAX_RETRIES = 10
MIN_RETRY_DELAY_SEC = 3.0
MIN_INTERVAL_SEC = 3.0

logger = logging.getLogger(__name__)


def handle_block_height_not_found(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code != 422:
                raise

            data = exc.response.json()
            error = data.get("error", {})
            cause = error.get("cause", {})

            if cause.get("name") != "UNKNOWN_BLOCK":
                raise

            block_height = (
                cause
                .get("info", {})
                .get("block_reference", {})
                .get("block_id")
            )

            raise BlockHeightNotFoundError(
                f"Block height {block_height} not found"
            ) from exc

    return wrapper


class RpcClient:
    RPC_MAINNET_URL = "https://rpc.mainnet.fastnear.com"
    ARCHIVAL_RPC_MAINNET_URL = "https://archival-rpc.mainnet.fastnear.com"

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    @retry(
        max_retries=MAX_RETRIES,
        min_retry_delay_sec=MIN_RETRY_DELAY_SEC,
        exceptions=(
            httpx.HTTPStatusError,
            httpx.ReadTimeout,
            httpx.RemoteProtocolError,
        ),
    )
    @rate_limit(
        min_interval_sec=MIN_INTERVAL_SEC,
    )
    @handle_block_height_not_found
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
            self.ARCHIVAL_RPC_MAINNET_URL,
            payload=payload,
        )

        result = data["result"]["result"]

        return bytes(result)

    @retry(
        max_retries=MAX_RETRIES,
        min_retry_delay_sec=MIN_RETRY_DELAY_SEC,
        exceptions=(
            httpx.HTTPStatusError,
            httpx.ReadTimeout,
            httpx.RemoteProtocolError,
        ),
    )
    @rate_limit(
        min_interval_sec=MIN_INTERVAL_SEC,
    )
    def fetch_final_block_height(self) -> int:

        block = self._fetch_block(
            url=self.RPC_MAINNET_URL,
            params={
                "finality": "final",
            }
        )

        return block["header"]["height"]

    @retry(
        max_retries=MAX_RETRIES,
        min_retry_delay_sec=MIN_RETRY_DELAY_SEC,
        exceptions=(
            httpx.HTTPStatusError,
            httpx.ReadTimeout,
            httpx.RemoteProtocolError,
        ),
    )
    @rate_limit(
        min_interval_sec=MIN_INTERVAL_SEC,
    )
    @handle_block_height_not_found
    def fetch_block_timestamp_nanoseconds(self, block_height: int) -> int:
        block = self._fetch_block(
            url=self.ARCHIVAL_RPC_MAINNET_URL,
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

    def _fetch_block(self, url: str, params: dict) -> dict:
        payload = {
            "jsonrpc": "2.0",
            "id": "staking",
            "method": "block",
            "params": params,
        }

        data = self._post(
            url=url,
            payload=payload,
        )

        return data["result"]

    def _post(self, url: str, payload: dict) -> dict:
        response = self._client.post(
            url=url,
            json=payload,
        )

        response.raise_for_status()
        data = response.json()

        if "error" in data:
            raise RuntimeError(
                f"NEAR RPC error: {data['error']}"
            )

        return data
