from sqlmodel import Field, SQLModel


class Key(SQLModel):
    account_key: str = Field(primary_key=True)
    pool_key: str = Field(primary_key=True)
