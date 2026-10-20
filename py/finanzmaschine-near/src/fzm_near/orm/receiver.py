from sqlmodel import Field, SQLModel


class Receiver(SQLModel, table=True):
    __tablename__ = "near_receivers"

    receiver_key: str = Field(primary_key=True)
    is_staking_pool: bool
