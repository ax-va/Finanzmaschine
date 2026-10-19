from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel


class Action(SQLModel, table=True):
    __tablename__ = "near_function_call_actions"

    receipt_key: str = Field(primary_key=True)
    action_index: int = Field(primary_key=True)

    # transaction singer key
    tx_signer_key: str = Field(index=True)
    # receipt predecessor key
    predecessor_key: str = Field(index=True)
    receiver_key: str = Field(index=True)
    tx_key: str = Field(index=True)

    tx_block_height: int = Field(
        index=True,
        sa_type=BigInteger,
    )
    receipt_block_height: int = Field(
        sa_type=BigInteger,
    )
    # receipt execution outcome block height
    exec_outcome_block_height: int = Field(
        index=True,
        sa_type=BigInteger,
    )

    # receipt execution outcome index
    exec_outcome_index: int
    method_name: str
    args_base64: str
    deposit_yocto_str: str
