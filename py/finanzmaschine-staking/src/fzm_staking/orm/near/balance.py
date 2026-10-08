from pydantic import field_validator
from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel


class Balance(SQLModel):
    block_height: int = Field(
        primary_key=True,
        foreign_key='near_blocks.block_height',
        sa_type=BigInteger,
    )

    staked_yocto_str: str
    unstaked_yocto_str: str

    @field_validator(
        'staked_yocto_str',
        'unstaked_yocto_str',
    )
    @classmethod
    def validate_yocto_str(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError(f"Balance yocto string must contain only digits: {value}")
        return value

    @property
    def staked_yocto(self) -> int:
        return int(self.staked_yocto_str)

    @property
    def unstaked_yocto(self) -> int:
        return int(self.unstaked_yocto_str)

    @property
    def total_yocto(self) -> int:
        return self.staked_yocto + self.unstaked_yocto
