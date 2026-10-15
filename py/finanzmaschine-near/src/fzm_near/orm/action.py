from enum import StrEnum

from sqlalchemy import BigInteger, Column, Enum
from sqlmodel import Field, SQLModel


class ActionType(StrEnum):
    FUNCTION_CALL = "FunctionCall"
    TRANSFER = "Transfer"


class Action(SQLModel, table=True):
    __tablename__ = "near_actions"

    receipt_key: str = Field(primary_key=True)
    action_index: int = Field(primary_key=True)

    transaction_key: str = Field(index=True)
    signer_key: str = Field(index=True)
    predecessor_key: str = Field(index=True)
    receiver_key: str = Field(index=True)

    tx_block_height: int = Field(
        index=True,
        sa_type=BigInteger,
    )
    receipt_block_height: int = Field(
        index=True,
        sa_type=BigInteger,
    )
    execution_outcome_block_height: int = Field(
        index=True,
        sa_type=BigInteger,
    )

    execution_outcome_index: int

    action_type: ActionType = Field(
        sa_column=Column(
            Enum(
                ActionType,
                values_callable=lambda enum: [item.value for item in enum],
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        )
    )
