import polars as pl
from sqlmodel import Session

from fzm_keying import KeyMapping
from fzm_near.helpers.staking.enums import MethodNameEnum
from fzm_near.helpers import constants as const
from fzm_near.helpers.staking.df_schemas import ACTION_SCHEMA
from fzm_near.orm.function_call.action import Action as FunctionCallAction
from fzm_near.helpers.staking.extractors import extract_operation_yocto_str
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

    def create_df_staking_actions(
        self,
        actions: list[FunctionCallAction],
    ) -> pl.DataFrame:
        """
        Filters function call actions and converts them into staking actions.

        Preserves the original action order and checks each unique receiver only once.

        Args:
            actions: Function call actions to process.

        Returns:
            Staking actions for verified staking pool receivers.
        """

        receiver_results: dict[str, bool] = {}
        rows: list[dict] = []

        for action in actions:
            try:
                method_name = MethodNameEnum(action.method_name)
            except ValueError:
                continue

            receiver_key = action.receiver_key

            if receiver_key not in receiver_results:
                receiver_results[receiver_key] = (
                    self._receiver_service.is_staking_pool(receiver_key)
                )

            if not receiver_results[receiver_key]:
                continue

            rows.append(
                {
                    const.RECEIPT_KEY: action.receipt_key,
                    const.ACTION_INDEX: action.action_index,
                    const.ACCOUNT_KEY: action.tx_signer_key,
                    const.POOL_KEY: action.receiver_key,
                    const.EXEC_OUTCOME_BLOCK_HEIGHT: action.exec_outcome_block_height,
                    const.EXEC_OUTCOME_INDEX: action.exec_outcome_index,
                    const.METHOD_NAME: method_name.value,
                    const.OPERATION_YOCTO_STR: extract_operation_yocto_str(action=action),
                }
            )

        return pl.DataFrame(
            data=rows,
            schema=ACTION_SCHEMA,
        )
