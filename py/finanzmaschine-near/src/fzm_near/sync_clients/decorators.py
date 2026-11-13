import functools
import logging
import time

import httpx

from fzm_near.sync_clients.errors import BlockHeightNotFoundError

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


def retry(
    max_retries: int,
    min_retry_delay_sec: float | int,
    exceptions: type[Exception] | tuple[type[Exception], ...],
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for retry_number in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions:
                    delay = min_retry_delay_sec * retry_number

                    logger.warning(
                        f"Retrying in {delay} seconds. "
                        f"Retry: {retry_number}/{max_retries}"
                    )

                    time.sleep(delay)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def rate_limit(min_interval_sec: float | int):
    def decorator(func):
        last_call_time = 0.0

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_call_time

            elapsed = time.monotonic() - last_call_time
            delay = min_interval_sec - elapsed

            if delay > 0:
                time.sleep(delay)

            last_call_time = time.monotonic()

            return func(*args, **kwargs)

        return wrapper

    return decorator
