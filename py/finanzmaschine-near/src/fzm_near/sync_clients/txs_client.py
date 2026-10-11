import httpx


class TxsClient:
    _TX_MAIN_URL = "https://tx.main.fastnear.com"
    _PAGE_LIMIT = 200
    _TXS_BATCH_SIZE = 20

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def fetch_account_txs(
        self,
        account_id: str,
        from_tx_block_height: int | None = None,
        up_to_tx_block_height: int | None = None,
        is_function_call: bool | None = None,
        is_success: bool | None = None,
        desc: bool = False,
    ) -> list[dict]:
        """
        Fetches transactions signed by a NEAR account.

        Retrieves all matching transactions, automatically following pagination
        using the resume token returned by the API.

        Args:
            account_id: NEAR account ID to fetch transactions for.
            from_tx_block_height:
                Minimum transaction block height, inclusive.
                If `None`, no lower bound is applied.
            up_to_tx_block_height:
                Maximum transaction block height, inclusive.
                If `None`, no upper bound is applied.
            is_function_call:
                Whether to filter transactions by FunctionCall involvement.
                If `None`, no FunctionCall filter is applied.
            is_success:
                Whether to filter transactions by successful execution.
                If `None`, no success filter is applied.
            desc: Whether to return transactions in descending order.

        Returns:
            All matching transaction records returned by the API.

        Raises:
            ValueError:
                If `lower_block_height` exceeds `upper_block_height`.
            httpx.HTTPStatusError:
                If an API request returns an unsuccessful HTTP status code.
        """

        if (
            from_tx_block_height is not None
            and up_to_tx_block_height is not None
            and from_tx_block_height > up_to_tx_block_height
        ):
            raise ValueError(
                "`from_tx_block_height` must not exceed `upper_block_height`"
            )

        account_txs: list[dict] = []

        payload = {
            "account_id": account_id,
            "is_signer": True,
            "limit": self._PAGE_LIMIT,
            "desc": desc,
        }

        if from_tx_block_height is not None:
            # `from_tx_block_height` is inclusive
            shifted_block_height = from_tx_block_height - 1
            # `payload["from_tx_block_height"]` must be exclusive
            payload["from_tx_block_height"] = shifted_block_height

        if up_to_tx_block_height is not None:
            # `up_to_tx_block_height` and `payload["to_tx_block_height"]` are inclusive
            payload["to_tx_block_height"] = up_to_tx_block_height

        if is_function_call is not None:
            payload["is_function_call"] = is_function_call

        if is_success is not None:
            payload["is_success"] = is_success

        while True:
            response = self._client.post(
                f"{self._TX_MAIN_URL}/v0/account",
                json=payload,
            )
            response.raise_for_status()

            data = response.json()
            account_txs.extend(data.get("account_txs", []))

            resume_token: str | None = data.get("resume_token")

            if not resume_token:
                break

            payload["resume_token"] = resume_token

        return account_txs

    def fetch_raw_txs(
        self,
        tx_hashes: list[str],
    ) -> list[dict]:
        """
        Fetch raw transactions by their hashes.

        Requests transactions in batches according to the API batch size limit.

        Args:
            tx_hashes: Transaction hashes to fetch.

        Returns:
            Raw transaction records returned by the API.

        Raises:
            httpx.HTTPStatusError: If an API request returns an unsuccessful HTTP status code.
        """
        raw_txs: list[dict] = []

        for i in range(0, len(tx_hashes), self._TXS_BATCH_SIZE):
            response = self._client.post(
                f"{self._TX_MAIN_URL}/v0/transactions",
                json={"tx_hashes": tx_hashes[i : i + self._TXS_BATCH_SIZE]},
            )
            response.raise_for_status()
            data = response.json()
            raw_txs.extend(data["transactions"])

        return raw_txs
