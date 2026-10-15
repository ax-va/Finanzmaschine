from fzm_keying import KeyMapping
from fzm_near.orm.function_call_action import FunctionCallAction


def create_actions(
    raw_txs: list[dict],
    key_mapping: KeyMapping,
) -> dict[str, list]:
    function_calls: list[FunctionCallAction] = []

    for raw_tx in raw_txs:
        transaction = raw_tx["transaction"]
        tx_outcome = raw_tx["execution_outcome"]

        transaction_key = key_mapping.get_key(transaction["hash"])
        signer_key = key_mapping.get_key(transaction["signer_id"])

        for raw_receipt in raw_tx["receipts"]:
            receipt = raw_receipt["receipt"]
            outcome = raw_receipt["execution_outcome"]

            action_receipt = receipt["receipt"].get("Action")
            if action_receipt is None:
                continue

            if "Failure" in outcome["outcome"]["status"]:
                continue

            receipt_key = key_mapping.get_key(receipt["receipt_id"])
            predecessor_key = key_mapping.get_key(receipt["predecessor_id"])
            receiver_key = key_mapping.get_key(receipt["receiver_id"])

            for action_index, raw_action in enumerate(action_receipt["actions"]):
                function_call = raw_action.get("FunctionCall")
                if function_call is None:
                    continue

                function_calls.append(
                    FunctionCallAction(
                        receipt_key=receipt_key,
                        action_index=action_index,
                        transaction_key=transaction_key,
                        signer_key=signer_key,
                        predecessor_key=predecessor_key,
                        receiver_key=receiver_key,
                        tx_block_height=tx_outcome["block_height"],
                        receipt_block_height=receipt["block_height"],
                        execution_outcome_block_height=outcome["block_height"],
                        execution_outcome_index=outcome["index"],
                        method_name=function_call["method_name"],
                        args_base64=function_call["args"],
                        deposit_yocto_str=function_call["deposit"],
                    )
                )

    function_calls.sort(
        key=lambda action: (
            action.execution_outcome_block_height,
            action.execution_outcome_index,
            action.action_index,
        )
    )

    return {
        "function_calls": function_calls,
    }