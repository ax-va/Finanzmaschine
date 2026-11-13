from sqlmodel import Field, SQLModel


class Receiver(SQLModel, table=True):
    """Stores a NEAR function call receiver."""

    __tablename__ = "near_function_call_receivers"

    receiver_key: str = Field(primary_key=True)
    is_staking_pool: bool
