from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel


class ActionSearch(SQLModel, table=True):
    __tablename__ = "near_function_call_action_searches"

    tx_signer_key: str = Field(primary_key=True)

    # inclusive block height
    up_to_tx_block_height: int | None = Field(
        default=None,
        sa_type=BigInteger,
    )

    is_locked: bool = Field(default=False)
