from functools import lru_cache

from finanzmaschine_staking.orm.near.block import Block
from finanzmaschine_staking.sync_clients.near.rpc_client import RpcClient


class BlockClient:
    def __init__(self, rpc_client: RpcClient) -> None:
        self._rpc_client = rpc_client

    @property
    def rpc_client(self) -> RpcClient:
        return self._rpc_client

    @lru_cache(maxsize=4096)
    def get_block(self, block_height: int) -> Block:
        timestamp_nanoseconds = self._rpc_client.get_block_timestamp_nanoseconds(block_height)

        return Block(
            block_height=block_height,
            timestamp_nanoseconds=timestamp_nanoseconds,
        )