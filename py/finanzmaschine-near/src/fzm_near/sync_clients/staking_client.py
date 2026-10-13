import json

from fzm_near.orm.staking_balance import StakingBalance
from fzm_near.sync_clients.rpc_client import RpcClient


class StakingClient:
    def __init__(self, rpc_client: RpcClient) -> None:
        self._rpc_client = rpc_client

    @property
    def rpc_client(self) -> RpcClient:
        return self._rpc_client

    def fetch_balance(
        self,
        account_id: str,
        pool_id: str,
        block_height: int,
    ) -> StakingBalance:
        """
        Gets a staking balance snapshot at a given block height.
        Uses LRU cache.

        Args:
            account_id: NEAR account ID whose staking balance is queried.
            pool_id: NEAR staking pool contact ID.
            block_height: Block height at which to query the staking balance.

        Returns:
            Staking balance snapshot containing
            the staked and unstaked balances at the specified block height.
        """
        staked_balance: str = self._fetch_balance(
            account_id=account_id,
            pool_id=pool_id,
            block_height=block_height,
            method_name="get_account_staked_balance",
        )

        unstaked_balance: str = self._fetch_balance(
            account_id=account_id,
            pool_id=pool_id,
            block_height=block_height,
            method_name="get_account_unstaked_balance",
        )

        return StakingBalance(
            block_height=block_height,
            staked_yocto_str=staked_balance,
            unstaked_yocto_str=unstaked_balance,
        )

    def _fetch_balance(
        self,
        account_id: str,
        pool_id: str,
        block_height: int,
        method_name: str,
    ) -> str:
        raw: bytes = self._rpc_client.call_view_function(
            contract_id=pool_id,
            method_name=method_name,
            args={"account_id": account_id},
            block_height=block_height,
        )

        value = json.loads(raw.decode())

        if not isinstance(value, str):
            raise RuntimeError(f"Expected balance must be a string, got: {value!r}")

        return value