from typing import Protocol


class RpcClientProtocol(Protocol):
    def call_view_function(
        self,
        contract_id: str,
        method_name: str,
        args: dict,
        block_height: int,
    ) -> bytes:
        ...

    def fetch_block_timestamp_nanoseconds(self, block_height: int) -> int:
        ...