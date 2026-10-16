from fzm_keying import KeyMapping
from fzm_near.orm.fucntiocn_call.action import Action


def create_actions(
    txs: dict[str, list[dict]],
    key_mapping: KeyMapping,
) -> dict[str, list]:
    function_calls: list[Action] = []

    for account_tx, raw_tx in zip(
            txs["account_txs"],
            txs["raw_txs"],
            strict=True,
    ):
        tx = raw_tx["transaction"]

        if account_tx["transaction_hash"] != tx["hash"]:
            raise ValueError(
                f"Mismatched `account_tx` and `raw_tx` "
                f"with different transaction hashes: %s and %s",
                key_mapping.get_value(account_tx["transaction_hash"]),
                key_mapping.get_value(tx["hash"]),
            )

        tx_block_height = account_tx["tx_block_height"]

        tx_key = key_mapping.get_key(tx["hash"])
        tx_signer_key = key_mapping.get_key(tx["signer_id"])

        for raw_receipt in raw_tx["receipts"]:
            receipt = raw_receipt["receipt"]
            receipt_outcome = raw_receipt["execution_outcome"]

            action_receipt = receipt["receipt"].get("Action")
            if action_receipt is None:
                continue

            if "Failure" in receipt_outcome["outcome"]["status"]:
                continue

            receipt_key = key_mapping.get_key(receipt["receipt_id"])
            receipt_predecessor_key = key_mapping.get_key(receipt["predecessor_id"])
            receiver_key = key_mapping.get_key(receipt["receiver_id"])

            for action_index, raw_action in enumerate(action_receipt["actions"]):

                function_call = raw_action.get("FunctionCall")
                if function_call is not None:
                    function_calls.append(
                        Action(
                            receipt_key=receipt_key,
                            action_index=action_index,
                            tx_key=tx_key,
                            tx_signer_key=tx_signer_key,
                            receipt_predecessor_key=receipt_predecessor_key,
                            receiver_key=receiver_key,
                            tx_block_height=tx_block_height,
                            receipt_block_height=receipt["block_height"],
                            receipt_execution_outcome_block_height=receipt_outcome["block_height"],
                            receipt_execution_outcome_index=receipt_outcome["index"],
                            method_name=function_call["method_name"],
                            args_base64=function_call["args"],
                            deposit_yocto_str=function_call["deposit"],
                        )
                    )

    function_calls.sort(
        key=lambda action: (
            action.receipt_execution_outcome_block_height,
            action.receipt_execution_outcome_index,
            action.action_index,
        )
    )

    return {
        "function_calls": function_calls,
    }