import os
from pathlib import Path
from uuid import uuid4

import polars as pl
from filelock import FileLock

from finanzmaschine_keying.key_mapping import KeyMapping
from finanzmaschine_keying.key_mapping_exceptions import KeyMappingIntegrityError


class CsvKeyMapping(KeyMapping):
    SCHEMA = {
        "key": pl.String,
        "value": pl.String,
    }

    def __init__(self, file_path: str | Path) -> None:
        self._file_path = Path(file_path)
        self._lock = FileLock(f"{self._file_path}.lock")

    def get_key(self, value: str) -> str:
        with self._lock:
            df = self._read()
            df_match = df.filter(pl.col("value") == value)

            if not df_match.is_empty():
                return df_match.item(0, "key")

            key = str(uuid4())

            df = pl.concat([
                df,
                pl.DataFrame(
                    {"key": [key], "value": [value]},
                    schema=self.SCHEMA,
                ),
            ])

            self._write(df)

            return key

    def get_value(self, key: str) -> str:
        with self._lock:
            df = self._read()
            df_match = df.filter(pl.col("key") == key)

            if df_match.is_empty():
                raise KeyError(f"Key {key!r} not found")

            return df_match.item(0, "value")

    def _read(self) -> pl.DataFrame:
        if not self._file_path.exists():
            return pl.DataFrame(schema=self.SCHEMA)

        df = pl.read_csv(
            self._file_path,
            schema=self.SCHEMA,
        )
        self._validate_integrity(df)

        return df

    def _write(self, df: pl.DataFrame) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

        temp_path = self._file_path.with_suffix(
            self._file_path.suffix + ".tmp"
        )

        try:
            df.write_csv(temp_path)
            os.replace(temp_path, self._file_path)
        finally:
            temp_path.unlink(missing_ok=True)

    @staticmethod
    def _validate_integrity(df: pl.DataFrame) -> None:
        if df["key"].n_unique() != df.height:
            raise KeyMappingIntegrityError("Duplicate keys")

        if df["value"].n_unique() != df.height:
            raise KeyMappingIntegrityError("Duplicate values")
