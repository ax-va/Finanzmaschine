from dataclasses import dataclass
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


@dataclass
class Action:
    """Represents a staking action derived from a NEAR function call action."""

    receipt_key: str
    action_index: int
    account_key: str
    pool_key: str
    exec_outcome_block_height: int
    method_name: MethodName
    operation_yocto: int | None
