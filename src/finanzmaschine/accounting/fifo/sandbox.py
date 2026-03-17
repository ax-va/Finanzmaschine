import polars as pl

from finanzmaschine.config import PRIVATE_DATA_DIR

df = pl.read_csv(
    PRIVATE_DATA_DIR / "trades" / "etps" / "toncoin.csv",
    try_parse_dates=True,
).sort("datetime")

df = df.with_columns(
    (pl.col("quantity") * pl.col("price")).round(2).alias("quantity * price"),
).select(
    [
        "datetime",
        "quantity",
        "price",
        "quantity * price",
        "fee",
        "total",
        "currency",
        "side",
    ]
)
pl.Config.set_tbl_rows(-1)
pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_width_chars(200)
print(df)
