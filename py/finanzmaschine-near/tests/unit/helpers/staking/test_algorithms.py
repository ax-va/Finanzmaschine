import pytest

from fzm_near.helpers.staking.algorithms import find_increased_balance
from fzm_near.orm.staking.balance import Balance
from tests.unit.helpers.staking.fake_balance_fetcher import FakeBalanceFetcher


def is_missing_block(block_height: int) -> bool:
    return (
        block_height % 7 == 0
        or block_height % 11 == 0
        or block_height % 13 == 0
    )


def get_balance(block_height: int) -> Balance:
    staked_yocto = 100 + block_height // 100

    return Balance(
        block_height=block_height,
        staked_yocto_str=str(staked_yocto),
        unstaked_yocto_str="2",
    )


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
        # Missing blocks (for example, 650 and 651) inside the search interval
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
        get_balance=get_balance,
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
