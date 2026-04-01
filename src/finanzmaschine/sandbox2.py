import polars as pl

from finanzmaschine.config import DATA_DIR_PATH

df = pl.read_csv(
    DATA_DIR_PATH / "private" / "trades" / "etps" / "toncoin.csv",
    try_parse_dates=True,
).sort("datetime")

df = df.with_columns(
    (pl.col("quantity") * pl.col("price")).round(2).alias("gross_value"),
).select(
    [
        "datetime",
        "base_asset",
        "quantity",
        "quote_asset",
        "price",
        "gross_value",
        "fee",
        "direction",
        "cash_flow",
        "action",
    ]
)
pl.Config.set_tbl_rows(-1)
pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_width_chars(200)
print(df)
