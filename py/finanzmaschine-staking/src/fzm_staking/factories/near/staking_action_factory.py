import base64
import binascii
import json

from fzm_keying import KeyMapping
from fzm_staking.orm.near.staking_action import StakingAction, StakingActionType


def create_staking_actions(
    raw_txs: list[dict],
    key_mapping: KeyMapping,
) -> list[StakingAction]:

    staking_actions: list[StakingAction] = []

    for raw_tx in raw_txs:
        if _contains_staking_action(raw_tx):
            staking_actions.extend(
                _create_staking_actions(raw_tx, key_mapping)
            )

    return staking_actions


def _create_staking_actions(
    raw_tx: dict,
    key_mapping: KeyMapping,
) -> list[StakingAction]:
    """Create staking actions from the transaction's successful initial receipts."""

    transaction = raw_tx["transaction"]

    receipt_ids = raw_tx["execution_outcome"]["outcome"]["receipt_ids"]
    receipts_by_id = {
        item["receipt"]["receipt_id"]: item
        for item in raw_tx["receipts"]
    }

    staking_actions: list[StakingAction] = []

    for receipt_id in receipt_ids:
        receipt = receipts_by_id.get(receipt_id)

        if receipt is None:
            raise RuntimeError(f"Receipt {receipt_id} not found")

        receipt_data = receipt["receipt"]
        action_receipt = receipt_data["receipt"].get("Action")

        if action_receipt is None:
            continue

        recognized_actions = []

        for action_index, action in enumerate(action_receipt["actions"]):
            function_call = action.get("FunctionCall")
            if function_call is None:
                continue

            try:
                action_type = StakingActionType(function_call.get("method_name"))
            except (ValueError, TypeError):
                continue

            recognized_actions.append((action_index, function_call, action_type))

        if not recognized_actions:
            continue

        status = receipt["execution_outcome"]["outcome"]["status"]
        if not any(key in status for key in ("SuccessValue", "SuccessReceiptId")):
            raise RuntimeError(f"Staking receipt execution failed: {status}")

        for action_index, function_call, action_type in recognized_actions:
            staking_actions.append(
                StakingAction(
                    receipt_key=key_mapping.get_key(receipt_id),
                    action_index=action_index,
                    transaction_key=key_mapping.get_key(transaction["hash"]),
                    account_key=key_mapping.get_key(transaction["signer_id"]),
                    pool_key=key_mapping.get_key(receipt_data["receiver_id"]),
                    tx_block_height=raw_tx["execution_outcome"]["block_height"],
                    receipt_block_height=receipt["execution_outcome"]["block_height"],
                    action_type=action_type,
                    operation_yocto_str=_extract_operation_yocto_str(
                        function_call,
                        action_type,
                    ),
                )
            )

    return staking_actions


def _contains_staking_action(raw_tx: dict) -> bool:
    """Check whether the transaction contains any recognized staking FunctionCall."""

    for action in raw_tx["transaction"].get("actions", []):
        function_call = action.get("FunctionCall")

        if function_call is None:
            continue

        try:
            StakingActionType(function_call.get("method_name"))
        except (ValueError, TypeError):
            continue

        return True

    return False


def _extract_operation_yocto_str(
    function_call: dict,
    action_type: StakingActionType,
) -> str | None:
    """Extract the requested staking quantity in yoctoNEAR."""
    if action_type in (
        StakingActionType.DEPOSIT,
        StakingActionType.DEPOSIT_AND_STAKE,
    ):
        quantity = function_call["deposit"]

    elif action_type in (
        StakingActionType.STAKE,
        StakingActionType.UNSTAKE,
        StakingActionType.WITHDRAW,
    ):
        try:
            decoded_args = base64.b64decode(
                function_call["args"],
                validate=True,
            )
            args = json.loads(decoded_args)
            quantity = args["amount"]

        except (
            KeyError,
            TypeError,
            ValueError,
            UnicodeDecodeError,
            binascii.Error,
        ) as exc:
            raise ValueError(
                f"Invalid FunctionCall arguments for {action_type.value}"
            ) from exc

    elif action_type in (
        StakingActionType.STAKE_ALL,
        StakingActionType.UNSTAKE_ALL,
        StakingActionType.WITHDRAW_ALL,
    ):
        return None

    else:
        raise ValueError(f"Unexpected staking action type: {action_type}")

    if (
        not isinstance(quantity, str)
        or not quantity.isascii()
        or not quantity.isdecimal()
    ):
        raise ValueError(
            f"Invalid quantity for {action_type.value}: {quantity!r}"
        )

    return quantity