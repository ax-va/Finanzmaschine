from typing import TypedDict

from fzm_staking.orm.near.staking_action import StakingActionType


class StakingActionData(TypedDict):
    receipt_id: str
    action_index: int
    transaction_hash: str
    account_id: str
    pool_id: str
    tx_block_height: int
    receipt_block_height: int
    action_type: StakingActionType
    operation_yocto_str: str | None
