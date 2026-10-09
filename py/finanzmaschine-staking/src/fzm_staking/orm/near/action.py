from enum import StrEnum

from pydantic import field_validator
from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel


class ActionType(StrEnum):
    DEPOSIT_AND_STAKE = "deposit_and_stake"
    DEPOSIT = "deposit"
    STAKE = "stake"
    STAKE_ALL = "stake_all"
    UNSTAKE = "unstake"
    UNSTAKE_ALL = "unstake_all"
    WITHDRAW = "withdraw"
    WITHDRAW_ALL = "withdraw_all"


class Action(SQLModel, table=True):
    __tablename__ = "near_staking_actions"

    receipt_key: str = Field(primary_key=True)
    action_index: int = Field(primary_key=True)
    transaction_key: str = Field(index=True)
    account_key: str = Field(index=True)
    pool_key: str = Field(index=True)

    tx_block_height: int = Field(
        foreign_key='near_blocks.block_height',
        index=True,
        sa_type=BigInteger,
    )

    receipt_block_height: int = Field(
        foreign_key='near_blocks.block_height',
        index=True,
        sa_type=BigInteger,
    )

    action_type: ActionType
    operation_yocto_str: str | None = None

    @field_validator("operation_yocto_str")
    @classmethod
    def validate_yocto_str(cls, value: str | None) -> str | None:
        if value is not None and not value.isdigit():
            raise ValueError(f"Operation yocto string must contain only digits: {value}")
        return value

    @property
    def operation_yocto(self) -> int | None:
        if self.operation_yocto_str is None:
            return None
        return int(self.operation_yocto_str)
