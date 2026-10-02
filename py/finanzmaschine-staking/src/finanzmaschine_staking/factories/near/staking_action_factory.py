from finanzmaschine_keying import KeyMapping
from finanzmaschine_staking.factories.near.staking_action_type import StakingActionData
from finanzmaschine_staking.orm.near.staking_action import StakingAction, StakingActionType


def create_staking_action(
    raw_tx: dict,
    key_mapping: KeyMapping,
) -> StakingAction:
    staking_action_data: StakingActionData = _extract_staking_action_data(raw_tx)

    return StakingAction(
        receipt_key=key_mapping.get_key(staking_action_data["receipt_id"]),
        transaction_key=key_mapping.get_key(staking_action_data["transaction_hash"]),
        account_key=key_mapping.get_key(staking_action_data["account_id"]),
        pool_id=staking_action_data["pool_id"],
        block_height=staking_action_data["block_height"],
        action_type=staking_action_data["action_type"],
        quantity_yocto_str=staking_action_data["quantity_yocto_str"],
    )


def is_staking_action(raw_tx: dict) -> bool:
    transaction: dict = raw_tx["transaction"]

    function_call: dict | None = _extract_function_call(transaction)
    if function_call is None:
        return False

    method_name: str | None = function_call.get("method_name")
    if method_name is None:
        return False

    try:
        StakingActionType(method_name)
    except (ValueError, TypeError):
        return False

    return True


def _extract_staking_action_data(raw_txs: dict) -> StakingActionData:
    transaction: dict = raw_txs["transaction"]

    function_call: dict | None = _extract_function_call(transaction)
    if function_call is None:
        raise RuntimeError(f"'FuctionCall' not found: {transaction}")

    method_name: str | None = function_call.get("method_name")
    if method_name is None:
        raise RuntimeError(f"'method_name' not found: {function_call}")

    try:
        action_type = StakingActionType(method_name)
    except (ValueError, TypeError):
        raise RuntimeError(f"{method_name!r} is not a valid staking action type")

    receipt_id: str = _extract_receipt_id(raw_tx)
    receipt: dict = _extract_receipt(raw_tx, receipt_id)

    return {
        "receipt_id": receipt_id,
        "transaction_hash": transaction["hash"],
        "account_id": transaction["signer_id"],
        "pool_id": transaction["receiver_id"],
        "block_height": receipt["execution_outcome"]["block_height"],
        "action_type": action_type,
        "quantity_yocto_str": _extract_quantity_yocto_str(function_call, action_type),
    }


def _extract_function_call(
    transaction: dict,
) -> dict | None:
    actions = transaction.get("actions", [])
    if len(actions) != 1:
        return None

    function_call = actions[0].get("FunctionCall")

    return function_call


def _extract_receipt_id(raw_tx: dict) -> str:
    receipt_ids = (
        raw_tx["execution_outcome"]
        ["outcome"]
        ["receipt_ids"]
    )

    if len(receipt_ids) != 1:
        raise RuntimeError(f"Expected exactly one receipt, got {receipt_ids}")

    return receipt_ids[0]


def _extract_receipt(
    raw_tx: dict,
    receipt_id: str,
) -> dict:
    for item in raw_tx["receipts"]:
        if item["receipt"]["receipt_id"] == receipt_id:
            return item

    raise RuntimeError(f"Receipt {receipt_id} not found")


def _extract_quantity_yocto_str(
    function_call: dict,
    action_type: StakingActionType,
) -> str | None:

    if action_type == StakingActionType.DEPOSIT_AND_STAKE:
        return function_call["deposit"]

    if action_type in (
        StakingActionType.STAKE_ALL,
        StakingActionType.UNSTAKE_ALL,
        StakingActionType.WITHDRAW_ALL,
    ):
        return None

    if action_type in (
        StakingActionType.DEPOSIT,
        StakingActionType.STAKE,
        StakingActionType.UNSTAKE,
        StakingActionType.WITHDRAW,
    ):
        # TODO: Add handling DEPOSIT, STAKE, UNSTAKE, WITHDRAW
        raise NotImplementedError(f"DEPOSIT, STAKE, UNSTAKE, and WITHDRAW not supported yet: {action_type}")

    raise RuntimeError(f"Unexpected staking action type: {action_type}")
