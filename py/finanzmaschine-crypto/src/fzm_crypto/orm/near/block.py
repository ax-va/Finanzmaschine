from datetime import datetime, timezone

from sqlalchemy import BigInteger
from sqlmodel import Field, SQLModel


class Block(SQLModel, table=True):
    __tablename__ = 'near_blocks'

    block_height: int = Field(
        primary_key=True,
        sa_type=BigInteger,
    )

    timestamp_nanoseconds: int = Field(
        sa_type=BigInteger,
    )

    @property
    def datetime_utc(self) -> datetime:
        seconds, nanoseconds = divmod(
            self.timestamp_nanoseconds, 1_000_000_000
        )

        return datetime.fromtimestamp(
            seconds,
            tz=timezone.utc,
        ).replace(microsecond=nanoseconds // 1_000)
