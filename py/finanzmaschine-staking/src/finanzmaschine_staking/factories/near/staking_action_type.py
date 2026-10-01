from typing import TypedDict

from finanzmaschine_staking.orm.near.staking_action import StakingActionType


class StakingActionData(TypedDict):
    receipt_id: str
    transaction_hash: str
    account_id: str
    pool_id: str
    block_height: int
    action_type: StakingActionType
    quantity_yocto_str: str | None
