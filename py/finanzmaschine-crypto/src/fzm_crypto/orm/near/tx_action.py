from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel


class TxAction(SQLModel, table=True):
    __tablename__ = "near_tx_actions"

    receipt_key: str = Field(primary_key=True)
    transaction_key: str = Field(index=True)
    account_key: str = Field(index=True)
    receiver_key: str = Field(index=True)

    block_height: int = Field(
        foreign_key='near_blocks.block_height',
        index=True,
        sa_type=BigInteger,
    )

    quantity_yocto_str: str | None = None
