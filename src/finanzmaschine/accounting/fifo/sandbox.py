import polars as pl

from finanzmaschine.config import DATA_DIR

df = pl.read_csv(
    DATA_DIR / "private" / "trades" / "etps" / "toncoin.csv",
    try_parse_dates=True,
).sort("datetime")

df = df.with_columns(
    (pl.col("quantity") * pl.col("price")).round(2).alias("quantity × price"),
).select(
    [
        "datetime",
        "base_asset",
        "quantity",
        "price",
        "quote_asset",
        "quantity × price",
        "fee",
        "fee_asset",
        "total",
        "total_asset",
        "side",
    ]
)
pl.Config.set_tbl_rows(-1)
pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_width_chars(200)
print(df)
