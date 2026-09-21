from sqlmodel import Session

from finanzmaschine_staking.orm.near.block import Block


class BlockRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, block_height: int) -> Block | None:
        return self._session.get(Block, block_height)

    def add(self, block: Block) -> None:
        self._session.add(block)
