from pydantic import BaseModel


class SnapshotMetadata(BaseModel):
    account_key: str
    pool_key: str
