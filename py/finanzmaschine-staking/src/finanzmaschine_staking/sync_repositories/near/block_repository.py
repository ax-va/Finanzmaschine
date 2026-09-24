from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from finanzmaschine_staking.orm.near.block import Block


class BlockRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def session(self):
        return self._session

    def get(self, block_height: int) -> Block | None:
        return self._session.get(Block, block_height)

    def add(self, block: Block) -> None:
        self._session.add(block)

    def flush(self) -> None:
        self._session.flush()

    def safe_add(self, block: Block) -> bool:
        try:
            with self._session.begin_nested():
                # savepoint
                self.add(block)
                self.flush()

            return True

        except IntegrityError:
            return False