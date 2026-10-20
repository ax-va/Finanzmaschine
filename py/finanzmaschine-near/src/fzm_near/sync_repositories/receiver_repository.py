from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from fzm_near.orm.receiver import Receiver
from fzm_near.sync_repositories.receiver_repository_errors import ReceiverRepositoryError


class ReceiverRepository:
    def __init__(self, session: Session):
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

    def get(self, receiver_key: str) -> Receiver | None:
        return self._session.get(Receiver, receiver_key)

    def add(self, receiver: Receiver) -> None:
        self._session.add(receiver)

    def flush(self) -> None:
        self._session.flush()

    def safe_add(self, receiver: Receiver) -> None:
        try:
            with self._session.begin_nested():
                # savepoint
                self.add(receiver)
                self.flush()

        except IntegrityError as e:
            # The savepoint transaction is rolled back
            receiver_: Receiver | None = self.get(
                receiver_key=receiver.receiver_key,
            )

            if receiver_ is not None:
                # The receiver failed to add
                # already exists in the database.
                return

            raise ReceiverRepositoryError(
                f"Cannot add receiver for receiver key: {receiver.receiver_key}"
            ) from e