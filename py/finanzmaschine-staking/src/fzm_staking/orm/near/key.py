from sqlmodel import Field, SQLModel


class Key(SQLModel):
    """Identifies a staking relationship between an account and a pool."""

    account_key: str = Field(primary_key=True)
    pool_key: str = Field(primary_key=True)
