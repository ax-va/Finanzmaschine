from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from fzm_near.helpers import constants as const
from fzm_near.helpers.staking.algorithms import find_increased_balance, find_increased_balances, find_snapshots
from fzm_near.helpers.staking.df_schemas import BALANCE_SCHEMA
from fzm_near.helpers.staking.errors import UnexpectedBalanceDecreaseError
from fzm_near.orm.staking.balance import Balance
from tests.unit.helpers.staking.data_loaders import load_expected_snapshot_balances
from tests.unit.helpers.staking.fake_balance_fetcher import FakeBalanceFetcher
from tests.unit.helpers.staking.fake_snapshot_storage import FakeSnapshotStorage


def is_missing_block(block_height: int) -> bool:
    return (
        block_height % 7 == 0
        or block_height % 11 == 0
        or block_height % 13 == 0
    )


def get_non_decreased_balance(block_height: int) -> Balance:
    if block_height < 3050:
        # Deposit and stake 101 YOCTO
        rewards_yocto = block_height // 100
        staked_yocto = 100 + rewards_yocto
        unstaked_yocto = 1

    elif block_height < 5050:
        # Deposit and stake 202 YOCTO at the block height 3050
        rewards_yocto = (block_height - 3000) // 100 * 3
        staked_yocto = 330 + rewards_yocto
        unstaked_yocto = 3

    elif block_height < 5251:
        # Deposit and stake 202 YOCTO at the block height 5050
        rewards_yocto = (block_height - 5000) // 100 * 5
        staked_yocto = 590 + rewards_yocto
        unstaked_yocto = 5

    elif block_height < 5550:
        # Deposit 202 YOCTO at the block height 5251
        rewards_yocto = (block_height - 5000) // 100 * 5
        staked_yocto = 590 + rewards_yocto
        unstaked_yocto = 207

    elif block_height < 6051:
        # Unstake all at the block height 5550
        staked_yocto = 0
        unstaked_yocto = 822

    else:
        # Deposit 202 YOCTO at the block height 6051
        staked_yocto = 0
        unstaked_yocto = 1024

    return Balance(
        block_height=block_height,
        staked_yocto_str=str(staked_yocto),
        unstaked_yocto_str=str(unstaked_yocto),
    )


def get_decreased_balance(block_height: int) -> Balance:
    staked_yocto = 100 if block_height < 200 else 99

    return Balance(
        block_height=block_height,
        staked_yocto_str=str(staked_yocto),
        unstaked_yocto_str="1",
    )


def balances_to_dataframe(balances: list[Balance]) -> pl.DataFrame:
    df = pl.DataFrame(
        [
            {
                "block_height": balance.block_height,
                "staked_yocto_str": balance.staked_yocto_str,
                "unstaked_yocto_str": balance.unstaked_yocto_str,
            }
            for balance in balances
        ],
        schema=BALANCE_SCHEMA,
    ).sort(const.BLOCK_HEIGHT)

    return df


@pytest.mark.parametrize(
    "start_block_height, "
    "up_to_block_height, "
    "expected_block_height",
    [
        # No balance increase
        (1, 99, None),
        # Increase at an existing block
        (1, 100, 100),
        # Multiple increases: find the first one
        (50, 250, 100),
        # Start after the first increase
        (101, 250, 200),
        # Missing blocks (for example, 649, 650, and 651) inside the search interval.
        (600, 699, None),
        # Block 700 is missing
        (600, 750, 701),
        # Upper boundary is missing
        (600, 700, None),
        # Increase at the upper boundary
        (600, 701, 701),
        # Two consecutive missing blocks at the reward boundary
        (2050, 2150, 2102),
        # Both missing blocks are at the upper end of the search range
        (2050, 2101, None),
        # First existing block with increased balance is the upper boundary
        (2050, 2102, 2102),
        # No increase before the second deposit
        (3001, 3049, None),
        # Second deposit at block 3050
        (3001, 3050, 3050),
        # Second deposit is the first increase in the interval
        (3001, 3099, 3050),
        # Regular reward after the second deposit
        (3050, 3100, 3100),
        # No increase between the second deposit and the next reward
        (3050, 3099, None),
        # No increase before the third deposit
        (5001, 5049, None),
        # Third deposit at block 5050
        (5001, 5050, 5050),
        # Third deposit is the first increase in the interval
        (5001, 5099, 5050),
        # Regular reward after the third deposit
        (5050, 5100, 5100),
        # No increase between the third deposit and the next reward
        (5050, 5099, None),
        # Fourth deposit at block 5251
        (5249, 5251, 5251),
        # No increase after the fourth deposit
        (5251, 5299, None),
        # First reward after the fourth deposit
        (5251, 5300, 5300),
        # Full unstake does not increase the total balance
        (5501, 5550, None),
        # No increase after the full unstake
        (5550, 6050, None),
        # Deposit after the full unstake
        (5550, 6051, 6051),
        # No rewards after deposit with the full unstake
        (6051, 6100, None),
    ],
)
def test_find_increased_balance(
    start_block_height: int,
    up_to_block_height: int,
    expected_block_height: int | None,
) -> None:
    account_id = "test_account"
    pool_id = "test_pool"

    fake_balance_fetcher = FakeBalanceFetcher(
        get_balance=get_non_decreased_balance,
        is_missing_block=is_missing_block,
    )

    start_block_balance: Balance = fake_balance_fetcher.fetch_balance(
        account_id=account_id,
        pool_id=pool_id,
        block_height=start_block_height,
    )

    fake_balance_fetcher.requested.clear()

    balance: Balance | None = find_increased_balance(
        account_id=account_id,
        pool_id=pool_id,
        start_block_balance=start_block_balance,
        up_to_block_height=up_to_block_height,
        balance_fetcher=fake_balance_fetcher,
    )

    if expected_block_height is None:
        assert balance is None

    else:
        assert balance is not None
        assert balance.block_height == expected_block_height
        assert start_block_balance.total_yocto < balance.total_yocto
        assert start_block_height < balance.block_height <= up_to_block_height

    for request in fake_balance_fetcher.requested:
        assert request["account_id"] == account_id
        assert request["pool_id"] == pool_id
        assert start_block_height < request["block_height"] <= up_to_block_height


def test_find_increased_balance_raises_on_balance_decrease() -> None:
    account_id = "test_account"
    pool_id = "test_pool"

    fake_balance_fetcher = FakeBalanceFetcher(
        get_balance=get_decreased_balance,
    )

    start_block_balance = fake_balance_fetcher.fetch_balance(
        account_id=account_id,
        pool_id=pool_id,
        block_height=100,
    )

    with pytest.raises(UnexpectedBalanceDecreaseError):
        find_increased_balance(
            account_id=account_id,
            pool_id=pool_id,
            start_block_balance=start_block_balance,
            up_to_block_height=300,
            balance_fetcher=fake_balance_fetcher,
        )


@pytest.mark.parametrize(
    "start_block_height, "
    "up_to_block_height",
    [
        # Upper boundary equals the start block height
        (100, 100),
        # Upper boundary is below the start block height
        (100, 99),
    ],
)
def test_find_increased_balance_raises_on_invalid_block_range(
    start_block_height: int,
    up_to_block_height: int,
) -> None:
    account_id = "test_account"
    pool_id = "test_pool"

    fake_balance_fetcher = FakeBalanceFetcher(
        get_balance=get_non_decreased_balance,
    )

    start_block_balance = fake_balance_fetcher.fetch_balance(
        account_id=account_id,
        pool_id=pool_id,
        block_height=start_block_height,
    )

    fake_balance_fetcher.requested.clear()

    with pytest.raises(ValueError):
        find_increased_balance(
            account_id=account_id,
            pool_id=pool_id,
            start_block_balance=start_block_balance,
            up_to_block_height=up_to_block_height,
            balance_fetcher=fake_balance_fetcher,
        )

    assert fake_balance_fetcher.requested == []


@pytest.mark.parametrize(
    "start_block_height, "
    "up_to_block_height, "
    "expected_block_heights",
    [
        # No balance increases
        (1, 99, []),
        # Single balance increase
        (1, 100, [100]),
        # Multiple balance increases
        (50, 350, [100, 200, 300]),
        # Start after the first increase
        (101, 350, [200, 300]),
        # Missing blocks inside the search interval
        (600, 699, []),
        # Reward increase at a missing block
        (600, 750, [701]),
        # Upper boundary is missing
        (600, 700, []),
        # Increase at the upper boundary
        (600, 701, [701]),
        # Multiple increases with missing reward blocks
        (600, 950, [701, 800, 900]),
        # Two consecutive missing blocks at the reward boundary
        (2050, 2150, [2102]),
        # Missing blocks at the upper end of the search range
        (2050, 2101, []),
        # First existing increased balance is the upper boundary
        (2050, 2102, [2102]),
        # Single-block interval without an increase
        (101, 102, []),
        # Single-block search interval
        (199, 200, [200]),
        # Increase immediately after the start block
        (199, 201, [200]),
        # Start block is itself a reward boundary
        (100, 201, [200]),
        # Upper boundary is immediately before the next increase
        (100, 199, []),
        # Multiple increases with the last one at the upper boundary
        (50, 300, [100, 200, 300]),
        # Multiple increases with the last one before the upper boundary
        (50, 301, [100, 200, 300]),
        # Missing block immediately after the start
        (97, 101, [100]),
        # No existing blocks after the start
        (97, 98, []),
        # Multiple increases after consecutive missing blocks
        (2050, 2250, [2102, 2201]),
        # No increase before the second deposit
        (3001, 3049, []),
        # Second deposit at block 3050
        (3001, 3050, [3050]),
        # Second deposit followed by a regular reward
        (3049, 3100, [3050, 3100]),
        # No increase between the second deposit and the next reward
        (3050, 3099, []),
        # Regular reward after the second deposit
        (3050, 3100, [3100]),
        # No increase before the third deposit
        (5001, 5048, []),
        # Third deposit at block 5050
        (5001, 5050, [5050]),
        # Third deposit followed by a regular reward
        (5001, 5100, [5050, 5100]),
        # No increase between the third deposit and the next reward
        (5050, 5099, []),
        # Regular reward after the third deposit
        (5050, 5100, [5100]),
        # Multiple rewards followed by the fourth deposit
        (5050, 5251, [5100, 5202, 5251]),
        # Fourth deposit at block 5251
        (5249, 5251, [5251]),
        # Fourth deposit and rewards before the full unstake at block 5550
        (5249, 5549, [5251, 5300, 5400, 5501]),
        # Fourth deposit and rewards with the full unstake at block 5550
        (5249, 5550, [5251, 5300, 5400, 5501]),
        # Increases including fourth deposit and rewards before the fifth deposit at block 6051
        (5249, 6050, [5251, 5300, 5400, 5501]),
        # Full unstake is the only event in the interval
        (5549, 5550, []),
        # No increase after the full unstake at 5550 and before the fifth deposit at block 6051
        (5550, 6050, []),
        # The fifth deposit after the full unstake
        (5550, 6051, [6051]),
        # No increases after the fifth deposit
        (6051, 6100, []),
        # All increases
        pytest.param(1, 6100,
            [
                100, 200, 300, 400, 500, 600, 701, 800, 900,
                1000, 1101, 1200, 1301, 1401, 1500, 1600, 1700, 1800, 1900,
                2000, 2102, 2201, 2300, 2400, 2500, 2601, 2700, 2801, 2900,
                3000, 3050,3100, 3200, 3301, 3400, 3501, 3600, 3700, 3800, 3901,
                4000, 4100, 4201, 4300, 4401, 4500, 4600, 4700, 4800, 4902,
                5000, 5050, 5100, 5202, 5251, 5300, 5400, 5501,
                6051,
            ],
            id="all-increases"
        )
    ],
)
def test_find_increased_balances(
    start_block_height: int,
    up_to_block_height: int,
    expected_block_heights: list[int],
) -> None:
    account_id = "test_account"
    pool_id = "test_pool"

    fake_balance_fetcher = FakeBalanceFetcher(
        get_balance=get_non_decreased_balance,
        is_missing_block=is_missing_block,
    )

    start_block_balance = fake_balance_fetcher.fetch_balance(
        account_id=account_id,
        pool_id=pool_id,
        block_height=start_block_height,
    )

    fake_balance_fetcher.requested.clear()

    balances: list[Balance] = find_increased_balances(
        account_id=account_id,
        pool_id=pool_id,
        start_block_balance=start_block_balance,
        up_to_block_height=up_to_block_height,
        balance_fetcher=fake_balance_fetcher,
    )

    assert (
        [balance.block_height for balance in balances]
        == expected_block_heights
    )

    previous_total_yocto = start_block_balance.total_yocto

    for balance in balances:
        assert previous_total_yocto < balance.total_yocto
        assert start_block_height < balance.block_height <= up_to_block_height
        previous_total_yocto = balance.total_yocto

    for request in fake_balance_fetcher.requested:
        assert request["account_id"] == account_id
        assert request["pool_id"] == pool_id
        assert start_block_height < request["block_height"] <= up_to_block_height


@pytest.mark.parametrize(
    "expected_balances_file, "
    "from_block_height, "
    "up_to_block_height, "
    "chunk_size",
    [
        (
            "snapshots/balances.csv",
            1,
            6100,
            1000,
        )
    ]
)
def test_find_snapshots(
    data_dir: Path,
    expected_balances_file: str,
    from_block_height: int,
    up_to_block_height: int,
    chunk_size: int,
) -> None:
    df_expected_balances: pl.DataFrame = load_expected_snapshot_balances(
        data_dir / "helpers/staking" / expected_balances_file,
    )

    account_id = "test_account"
    pool_id = "test_pool"

    fake_balance_fetcher = FakeBalanceFetcher(
        get_balance=get_non_decreased_balance,
        is_missing_block=is_missing_block,
    )

    fake_snapshot_storage = FakeSnapshotStorage()

    find_snapshots(
        account_id=account_id,
        pool_id=pool_id,
        from_block_height=from_block_height,
        up_to_block_height=up_to_block_height,
        balance_fetcher=fake_balance_fetcher,
        snapshot_storage=fake_snapshot_storage,
        chunk_size=chunk_size,
    )

    # Check the number of chunks
    assert len(fake_snapshot_storage.saved) == (
        (up_to_block_height - from_block_height) // chunk_size + 1
    )

    expected_chunk_lower: int = from_block_height

    # Check balances in each chunk
    while expected_chunk_lower <= up_to_block_height:
        expected_chunk_upper: int = min(
            up_to_block_height, expected_chunk_lower + chunk_size - 1
        )

        actual_chunk_balances: list[Balance] = fake_snapshot_storage.saved[
            (expected_chunk_lower, expected_chunk_upper)
        ]

        df_expected_chunk_balances: pl.DataFrame = df_expected_balances.filter(
            pl.col(const.BLOCK_HEIGHT).is_between(
                expected_chunk_lower,
                expected_chunk_upper,
            )
        )

        df_actual_chunk_balances: pl.DataFrame = (
            balances_to_dataframe(actual_chunk_balances)
        )

        assert_frame_equal(
            df_actual_chunk_balances,
            df_expected_chunk_balances,
        )

        expected_chunk_lower = expected_chunk_upper + 1

    # Check balances in all chunks
    df_actual_balances: pl.DataFrame = balances_to_dataframe(
        fake_snapshot_storage.saved_balances
    )

    assert_frame_equal(
        df_actual_balances,
        df_expected_balances,
    )

    # Check parameters when fetching
    for request in fake_balance_fetcher.requested:
        assert request["account_id"] == account_id
        assert request["pool_id"] == pool_id
        assert from_block_height <= request[const.BLOCK_HEIGHT] <= up_to_block_height
