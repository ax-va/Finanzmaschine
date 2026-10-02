import httpx


class TxsClient:
    TX_MAIN_URL = "https://tx.main.fastnear.com"
    PAGE_LIMIT = 200
    TXS_BATCH_SIZE = 20

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def fetch_function_calls(
        self,
        account_id: str,
        lower_height_excl: int | None = None,
        upper_height_incl: int | None = None,
        desc: bool = False,
    ) -> list[dict]:
        """
        Fetch success function-call transactions for an account.

        Retrieves all matching transactions, automatically following pagination
        using the resume token returned by the API.

        Args:
            account_id: NEAR account ID to fetch transactions for.
            lower_height_excl: Minimum transaction block height, exclusive. If `None`, no lower bound is applied.
            upper_height_incl: Maximum transaction block height, inclusive. If `None`, no upper bound is applied.
            desc: Whether to return transactions in descending order.

        Returns:
            All matching transaction records returned by the API.

        Raises:
            ValueError: If `page_limit` is outside the allowed range.
            httpx.HTTPStatusError: If an API request returns an unsuccessful HTTP status code.
        """

        account_txs: list[dict] = []

        payload = {
            "account_id": account_id,
            "is_signer": True,
            "is_fucntion_call": True,
            "is_success": True,
            "limit": self.PAGE_LIMIT,
            "desc": desc,
        }

        if lower_height_excl is not None:
            payload["from_tx_block_height"] = lower_height_excl

        if upper_height_incl is not None:
            payload["to_tx_block_height"] = upper_height_incl

        while True:
            response = self._client.post(
                f"{self.TX_MAIN_URL}/v0/account",
                json=payload,
            )
            response.raise_for_status()

            data = response.json()
            account_txs.extend(data.get("account_txs", []))

            resume_token: str | None = data.get("resume_token")

            if resume_token is None:
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

        for i in range(0, len(tx_hashes), self.TXS_BATCH_SIZE):
            response = self._client.post(
                f"{self.TX_MAIN_URL}/v0/transactions",
                json={"tx_hashes": tx_hashes[i : i + self.TXS_BATCH_SIZE]},
            )
            response.raise_for_status()
            data = response.json()
            raw_txs.extend(data["transactions"])

        return raw_txs
