from fzm_near.orm.block import Block
from fzm_near.sync_clients.fastnear_rpc_client import FastnearRpcClient


class BlockClient:
    def __init__(self, rpc_client: FastnearRpcClient) -> None:
        self._rpc_client = rpc_client

    @property
    def rpc_client(self) -> FastnearRpcClient:
        return self._rpc_client

    def fetch_block(self, block_height: int) -> Block:
        timestamp_nanoseconds = self._rpc_client.fetch_block_timestamp_nanoseconds(block_height)

        return Block(
            block_height=block_height,
            timestamp_nanoseconds=timestamp_nanoseconds,
        )
