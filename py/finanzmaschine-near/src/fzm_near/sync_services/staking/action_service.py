import polars as pl
from sqlmodel import Session

from fzm_keying import KeyMapping
from fzm_near.helpers.staking.enums import MethodNameEnum
from fzm_near.orm.function_call.action import Action as FunctionCallAction
from fzm_near.helpers.staking.factories import extract_operation_yocto_str
from fzm_near.sync_services.receiver_service import ReceiverService


class ActionService:

    ACTION_SCHEMA = {
        "receipt_key": pl.String,
        "action_index": pl.Int64,
        "account_key": pl.String,
        "pool_key": pl.String,
        "exec_outcome_block_height": pl.Int64,
        "exec_outcome_index": pl.Int64,
        "method_name": pl.String,
        "operation_yocto_str": pl.String,
    }

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
                dict(
                    receipt_key=action.receipt_key,
                    action_index=action.action_index,
                    account_key=action.tx_signer_key,
                    pool_key=action.receiver_key,
                    exec_outcome_block_height=action.exec_outcome_block_height,
                    method_name=method_name.value,
                    operation_yocto_str=extract_operation_yocto_str(action=action)
                )
            )

        return pl.DataFrame(
            data=rows,
            schema=self.ACTION_SCHEMA,
        )
