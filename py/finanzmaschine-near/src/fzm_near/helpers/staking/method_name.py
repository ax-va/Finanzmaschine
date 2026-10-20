from enum import StrEnum


class MethodName(StrEnum):
    """Supported staking pool methods."""

    DEPOSIT_AND_STAKE = "deposit_and_stake"
    DEPOSIT = "deposit"
    STAKE = "stake"
    STAKE_ALL = "stake_all"
    UNSTAKE = "unstake"
    UNSTAKE_ALL = "unstake_all"
    WITHDRAW = "withdraw"
    WITHDRAW_ALL = "withdraw_all"
