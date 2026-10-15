from enum import StrEnum

from pydantic import field_validator
from sqlalchemy import Column, Enum, ForeignKeyConstraint
from sqlmodel import Field, SQLModel


class MethodNameType(StrEnum):
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

    __table_args__ = (
        ForeignKeyConstraint(
            ["receipt_key", "action_index"],
            ["near_actions.receipt_key", "near_actions.action_index"],
        ),
    )

    receipt_key: str = Field(primary_key=True)
    action_index: int = Field(primary_key=True)

    method_name: MethodNameType = Field(
        sa_column=Column(
            Enum(
                MethodNameType,
                values_callable=lambda enum: [item.value for item in enum],
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        )
    )

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
