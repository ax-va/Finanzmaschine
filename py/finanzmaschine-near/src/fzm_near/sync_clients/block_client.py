from fzm_near.orm.block import Block
from fzm_near.sync_clients.protocols import RpcClientProtocol


class BlockClient:
    def __init__(self, rpc_client: RpcClientProtocol) -> None:
        self._rpc_client = rpc_client

    @property
    def rpc_client(self) -> RpcClientProtocol:
        return self._rpc_client

    def fetch_block(self, block_height: int) -> Block:
        timestamp_nanoseconds = self._rpc_client.fetch_block_timestamp_nanoseconds(block_height)

        return Block(
            block_height=block_height,
            timestamp_nanoseconds=timestamp_nanoseconds,
        )
