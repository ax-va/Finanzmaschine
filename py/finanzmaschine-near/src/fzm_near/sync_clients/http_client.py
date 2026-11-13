from typing import Any

import httpx

import fzm_near.sync_clients.constants as const
from fzm_near.sync_clients.decorators import (
    handle_block_height_not_found,
    rate_limit,
    retry,
)


class HttpClient:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    @retry(
        max_retries=const.MAX_RETRIES,
        min_retry_delay_sec=const.MIN_RETRY_DELAY_SEC,
        exceptions=(
            httpx.HTTPStatusError,
            httpx.ReadTimeout,
            httpx.RemoteProtocolError,
        ),
    )
    @rate_limit(
        min_interval_sec=const.MIN_INTERVAL_SEC,
    )
    @handle_block_height_not_found
    def _post(
        self,
        url: str,
        payload: dict[str, Any],
        error_name: str = "",
    ) -> dict[str, Any]:
        response = self._client.post(
            url=url,
            json=payload,
        )

        response.raise_for_status()
        data = response.json()

        if "error" in data:
            error_msg = data["error"]
            if error_name:
                error_msg = error_name + ": " + error_msg

            raise RuntimeError(error_msg)

        return data