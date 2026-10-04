import logging

from finanzmaschine_crypto.sync_clients.near.rpc_client_exeptions import BlockHeightNotFoundError
from finanzmaschine_staking.algorithms.near.binary_search_exceptions import UnexpectedBalanceDecreaseError
from finanzmaschine_staking.orm.near.balance import Balance
from finanzmaschine_staking.storage.near.snapshot_storage import SnapshotStorage
from finanzmaschine_staking.sync_clients.near.staking_client import StakingClient

logger = logging.getLogger(__name__)


def find_next_balance_increase(
    account_id: str,
    pool_id: str,
    lower_block_balance: Balance,
    upper_block_height: int,
    staking_client: StakingClient,
) -> Balance | None:
    """
    Finds the next total balance increase between
    the exclusive lower and inclusive upper block heights.

    The total balance is the sum of staked and unstaked balances.

    Returns `None`, if no balance increase is detected in the given interval.

    Search contract:
        The total balance must be monotonically non-decreasing over the searched interval.
        This condition is required for the binary search to be valid.

        This function is intended to search intervals
        where no staking action can decrease the total balance.

        If a total balance decrease is observed at any inspected block,
        `UnexpectedBalanceDecreaseError` is raised.

    Args:
        account_id: Account whose staking balance is being searched.
        pool_id: Staking pool associated with the account.
        lower_block_balance: Lower-block balance that sets the lower block height, exclusive.
        upper_block_height: Upper block height, inclusive.
        staking_client: NEAR staking client.

    Returns:
        The first balance with a total balance greater than `lower_block_balance.block_height`,
        or `None` if no increase is detected.

    Raises:
        ValueError:
            If `upper_block_height` is less than or equal to `lower_block_balance.block_height`.
        UnexpectedBalanceDecreaseError:
            If a total balance decrease is detected during the search.
    """
    logger.debug(
        f"Starting search for next balance increase between block heights "
        f"{lower_block_balance.block_height} and {upper_block_height}"
    )

    if upper_block_height <= lower_block_balance.block_height:
        raise ValueError(
            "`upper_block_height` must be greater than `lower_block_balance.block_height`"
        )

    while upper_block_height > lower_block_balance.block_height:

        try:
            upper_block_balance: Balance = staking_client.get_balance(
                account_id=account_id,
                pool_id=pool_id,
                block_height=upper_block_height,
            )

        except BlockHeightNotFoundError:
            logger.warning(f"Block height not found: {upper_block_height}")

            upper_block_height -= 1

        else:
            break

    else:
        logger.debug(
            f"No block found after block height {lower_block_balance.block_height}"
        )

        return None

    if (
        upper_block_balance.total_balance_yocto
        < lower_block_balance.total_balance_yocto
    ):
        raise UnexpectedBalanceDecreaseError(
            "Violation of the binary search contract: "
            f"`upper_block_balance.total_balance_yocto` of {upper_block_balance.total_balance_yocto} "
            f"is less than `lower_block_balance.total_balance_yocto` of {lower_block_balance.total_balance_yocto}"
        )

    elif (
        lower_block_balance.total_balance_yocto
        == upper_block_balance.total_balance_yocto
    ):
        logger.debug(
            f"No balance increase between block heights "
            f"{lower_block_balance.block_height} and {upper_block_height}"
        )

        return None

    while upper_block_balance.block_height - lower_block_balance.block_height > 1:
        logger.debug(
            f"Searching balance increase between block heights "
            f"{lower_block_balance.block_height} and {upper_block_balance.block_height}"
        )

        middle_block_height = (
            lower_block_balance.block_height
            + upper_block_balance.block_height
        ) // 2
        temp_upper_block_height = middle_block_height

        while lower_block_balance.block_height < temp_upper_block_height:
            try:
                temp_block_balance: Balance = staking_client.get_balance(
                    account_id=account_id,
                    pool_id=pool_id,
                    block_height=temp_upper_block_height,
                )

            except BlockHeightNotFoundError:
                logger.warning(f"Block height not found: {temp_upper_block_height}")

                temp_upper_block_height -= 1

            else:
                break

        else:
            temp_lower_block_height = middle_block_height + 1

            while temp_lower_block_height < upper_block_balance.block_height:
                try:
                    temp_block_balance: Balance = staking_client.get_balance(
                        account_id=account_id,
                        pool_id=pool_id,
                        block_height=temp_lower_block_height,
                    )

                except BlockHeightNotFoundError:
                    logger.warning(f"Block height not found: {temp_lower_block_height}")

                    temp_lower_block_height += 1

                else:
                    break

            else:
                logger.debug(
                    f"Found next balance increase at block height {upper_block_balance.block_height}"
                )

                return upper_block_balance

        if (
            temp_block_balance.total_balance_yocto
            < lower_block_balance.total_balance_yocto
        ):
            raise UnexpectedBalanceDecreaseError(
                "Violation of the binary search contract: "
                f"`temp_block_balance.total_balance_yocto` of {temp_block_balance.total_balance_yocto} "
                f"is less than `lower_block_balance.total_balance_yocto` of {lower_block_balance.total_balance_yocto}"
            )

        elif (
            lower_block_balance.total_balance_yocto
            == temp_block_balance.total_balance_yocto
        ):
            lower_block_balance = temp_block_balance

        else:
            upper_block_balance = temp_block_balance

    logger.debug(
        f"Found next balance increase at block height {upper_block_balance.block_height}"
    )

    return upper_block_balance


def find_balance_increases(
    account_id: str,
    pool_id: str,
    lower_block_balance: Balance,
    upper_block_height: int,
    staking_client: StakingClient,
) -> list[Balance]:
    """
    Finds all total balance increases between
    the exclusive lower and inclusive upper block heights.

    Repeatedly searches for the next balance whose total balance
    is greater than the previously found balance.

    Search contract:
        The search contract of `find_next_balance_increase`
        applies to the entire searched interval.

    Args:
        account_id: Account whose staking balance is being searched.
        pool_id: Staking pool associated with the account.
        lower_block_balance: Lower-block balance that sets the lower block height, exclusive.
        upper_block_height: Upper block height, inclusive.
        staking_client: NEAR staking client.

    Returns:
        The balances at which the total balance increases, ordered by block height.

    Raises:
        ValueError:
            If `upper_block_height` is less than or equal to `lower_block_balance.block_height`.
        UnexpectedBalanceDecreaseError:
            If a total balance decrease is detected at an inspected block.
    """
    balances: list[Balance] = []

    while True:
        next_balance: Balance | None = find_next_balance_increase(
            account_id=account_id,
            pool_id=pool_id,
            lower_block_balance=lower_block_balance,
            upper_block_height=upper_block_height,
            staking_client=staking_client,
        )

        if next_balance is None:
            break

        balances.append(next_balance)
        lower_block_balance = next_balance

    return balances


def find_staking_snapshots(
    account_id: str,
    pool_id: str,
    lower_block_height: int,
    upper_block_height: int,
    staking_client: StakingClient,
    snapshot_storage: SnapshotStorage,
    chunk_size: int = 1_000_000,
    last_known_balance: Balance | None = None,
) -> None:
    """
    Finds staking snapshots within a block range in fixed-size chunks.

    Splits the inclusive range from `lower_block_height` to `upper_block_height`
    into non-overlapping chunks and searches each chunk for balance increases.

    Each processed chaunk is saved to the `snapshot_storage.target_dir` directory,
    including chunks where no staking snapshots are found.

    If `last_known_balance` is not provided, the first existing balance in the search range
    is used as the initial baseline and included in the result.

    If `last_known_balance` is provided, chunks before its block height are skipped
    and the search resumes from that balance.

    Search contract:
        The search contract of `find_balance_increases`
        applies to the entire searched interval.

    Args:
        account_id: Account whose staking balance is being searched.
        pool_id: Staking pool associated with the account.
        lower_block_height: Lower block height, inclusive.
        upper_block_height: Upper block height, inclusive.
        staking_client: NEAR staking client.
        snapshot_storage: Temporal storage for metadata and found staking snapshots.
        chunk_size: Maximum block-height range covered by each chunk.
        last_known_balance:
            Last known balance preceding the search range.
            If omitted, the first available balance is treated
            as the initial baseline and is included in the result.

    Raises:
        ValueError:
            If `chunk_size` is less than or equal to zero.
            If `last_known_snapshot.block_height` is outside the
            inclusive `lower_block_height` and exclusive `upper_block_height` interval.
            From `find_balance_increases`.
        UnexpectedBalanceDecreaseError: From `find_balance_increases`.
    """
    if chunk_size <= 0:
        raise ValueError("`chunk_size` must be greater than 0")

    if last_known_balance is not None:

        if last_known_balance.block_height < lower_block_height:
            raise ValueError(
                f"`last_known_snapshot.block_height` must be greater than or equal to `lower_block_height`"
            )

        if upper_block_height <= last_known_balance.block_height:
            raise ValueError(
                f"`last_known_snapshot.block_height` must be less than `upper_block_height`"
            )

    logger.info(
        f"Starting global search for staking snapshots between block heights "
        f"{lower_block_height} and {upper_block_height}"
    )

    chunk_lower_block_height = lower_block_height

    while chunk_lower_block_height <= upper_block_height:

        snapshot_storage.clear()

        chunk_upper_block_height = min(
            chunk_lower_block_height + chunk_size - 1,
            upper_block_height,
        )

        if last_known_balance is not None:
            if chunk_upper_block_height <= last_known_balance.block_height:
                logger.info(
                    f"Skipping chunk search for staking snapshots between "
                    f"{chunk_lower_block_height} and {chunk_upper_block_height}"
                )

                chunk_lower_block_height = chunk_upper_block_height + 1
                continue

        else:
            logger.info(
                f"Searching the first existing balance between block heights "
                f"{chunk_lower_block_height} and {chunk_upper_block_height}"
            )

            block_height = chunk_lower_block_height

            while block_height <= chunk_upper_block_height:
                try:
                    last_known_balance: Balance = staking_client.get_balance(
                        account_id=account_id,
                        pool_id=pool_id,
                        block_height=block_height,
                    )
                    snapshot_storage.add(last_known_balance)
                    break

                except BlockHeightNotFoundError:
                    block_height += 1

        logger.info(
            f"Starting chunk search for staking snapshots between block heights "
            f"{chunk_lower_block_height} and {chunk_upper_block_height}"
        )

        if (
            last_known_balance is not None
            and last_known_balance.block_height < chunk_upper_block_height
        ):
            balances: list[Balance] = find_balance_increases(
                staking_client=staking_client,
                account_id=account_id,
                pool_id=pool_id,
                lower_block_balance=last_known_balance,
                upper_block_height=chunk_upper_block_height,
            )

            for balance in balances:
                snapshot_storage.add(balance)

            if balances:
                last_known_balance = balances[-1]

        logger.debug(
            f"Saving staking snapshots for chunk between block heights "
            f"{chunk_lower_block_height} and {chunk_upper_block_height}"
        )

        snapshot_storage.save(
            lower_block_height=chunk_lower_block_height,
            upper_block_height=chunk_upper_block_height,
        )

        chunk_lower_block_height = chunk_upper_block_height + 1

    logger.info("Global search completed")
