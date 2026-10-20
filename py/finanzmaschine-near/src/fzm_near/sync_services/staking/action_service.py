from sqlmodel import Session

from fzm_keying import KeyMapping
from fzm_near.helpers.staking.action import Action as StakingAction
from fzm_near.helpers.staking.action import MethodName
from fzm_near.orm.function_call.action import Action as FunctionCallAction
from fzm_near.helpers.staking.factories import extract_operation_yocto
from fzm_near.sync_services.receiver_service import ReceiverService


class ActionService:

    def __init__(
        self,
        session: Session,
        key_mapping: KeyMapping,
    ) -> None:

        self._session: Session = session
        self._key_mapping = key_mapping
        self._receiver_service = ReceiverService(
            session=session,
            key_mapping=key_mapping,
        )

    def create_staking_actions(
        self,
        actions: list[FunctionCallAction]
    ) -> list[StakingAction]:
        """
        Filters function call actions and converts them into staking actions.

        Preserves the original action order and checks each unique receiver only once.

        Args:
            actions: Function call actions to process.

        Returns:
            Staking actions for verified staking pool receivers.
        """

        receiver_results: dict[str, bool] = {}
        staking_actions: list[StakingAction] = []

        for action in actions:
            try:
                method_name = MethodName(action.method_name)
            except ValueError:
                continue

            receiver_key = action.receiver_key

            if receiver_key not in receiver_results:
                is_staking_pool: bool = self._receiver_service.is_staking_pool(receiver_key)
                receiver_results[receiver_key] = is_staking_pool

            if not receiver_results[receiver_key]:
                continue

            staking_actions.append(
                StakingAction(
                    receipt_key=action.receipt_key,
                    action_index=action.action_index,
                    account_key=action.tx_signer_key,
                    pool_key=action.receiver_key,
                    exec_outcome_block_height=action.exec_outcome_block_height,
                    method_name=method_name,
                    operation_yocto=extract_operation_yocto(action=action)
                )
            )

        return staking_actions
