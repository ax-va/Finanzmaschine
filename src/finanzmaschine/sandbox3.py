import polars as pl

from finanzmaschine.config import DATA_DIR_PATH

df = pl.read_csv(
    DATA_DIR_PATH / "private" / "trades" / "etps" / "toncoin.csv",
    try_parse_dates=True,
).sort("datetime")

for row in df.iter_rows(named=True):
