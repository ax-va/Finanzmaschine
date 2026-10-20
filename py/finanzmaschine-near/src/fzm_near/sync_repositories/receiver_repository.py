from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from fzm_near.orm.receiver import Receiver
from fzm_near.sync_repositories.receiver_repository_errors import ReceiverRepositoryError


class ReceiverRepository:
    """Manages receiver records in the database."""

    def __init__(self, session: Session):
        """
        Args:
            session: Database session.
        """
        self._session = session

    @property
    def session(self) -> Session:
        """Return the database session."""
        return self._session

    def get(self, receiver_key: str) -> Receiver | None:
        """
        Retrieves a receiver by its key.

        Args:
            receiver_key: Unique key identifying the receiver.

        Returns:
            The receiver if found, otherwise `None`.
        """
        return self._session.get(Receiver, receiver_key)

    def add(self, receiver: Receiver) -> None:
        """
        Adds a receiver to the database session.

        Args:
            receiver: Receiver to add.
        """
        self._session.add(receiver)

    def flush(self) -> None:
        """Flushes pending changes to the database."""
        self._session.flush()

    def safe_add(self, receiver: Receiver) -> Receiver:
        """
        Adds a receiver or return the existing record if it already exists.

        Uses a savepoint to handle integrity conflicts without rolling back
        the surrounding transaction.

        Args:
            receiver: Receiver to add.

        Returns:
            The added receiver or the existing receiver.

        Raises:
            ReceiverRepositoryError:
                If the receiver could not be added in the database.
        """
        try:
            with self._session.begin_nested():
                # savepoint
                self.add(receiver)
                self.flush()

            return receiver

        except IntegrityError as e:
            # The savepoint transaction is rolled back
            receiver_: Receiver | None = self.get(
                receiver_key=receiver.receiver_key,
            )

            if receiver_ is not None:
                # The receiver failed to add
                # already exists in the database.
                return receiver_

            raise ReceiverRepositoryError(
                f"Cannot add receiver for receiver key: {receiver.receiver_key}"
            ) from e