from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel


class Search(SQLModel, table=True):
    __tablename__ = "near_function_call_searches"

    account_key: str = Field(primary_key=True)

    # inclusive block height
    up_to_tx_block_height: int | None = Field(
        default=None,
        sa_type=BigInteger,
    )

    locked: bool = Field(default=False)
