import base64
import json

from fzm_near.helpers.staking.enums import MethodNameEnum
from fzm_near.orm.function_call.action import Action as FunctionCallAction


def extract_operation_yocto_str(action: FunctionCallAction) -> str | None:
    """
    Extracts the staking operation amount from a function call.

    Function contract:
        The function call action must be a staking action.

    Args:
        action: Function call action.

    Returns:
        The string with the operation YOCTO amount.
    """

    if action.method_name in {
        MethodNameEnum.DEPOSIT,
        MethodNameEnum.DEPOSIT_AND_STAKE,
    }:
        return action.deposit_yocto_str

    if action.method_name in {
        MethodNameEnum.STAKE,
        MethodNameEnum.UNSTAKE,
        MethodNameEnum.WITHDRAW,
    }:
        args = json.loads(base64.b64decode(action.args_base64))
        return str(args["amount"])

    return None
