import polars as pl

from finanzmaschine.config import DATA_DIR_PATH

df = pl.read_csv(
    DATA_DIR_PATH / "private" / "trades" / "etps" / "toncoin.csv",
    try_parse_dates=True,
    schema_overrides={
        "price": pl.String,
        "fee": pl.String,
        "base_asset_flow": pl.String,
        "quote_asset_flow": pl.String,
    },
).sort("datetime")

# df = df.with_columns(
#     (pl.col("base_asset_flow") * pl.col("price")).round(2).alias("signed_gross_value"),
# ).select(
#     [
#         "datetime",
#         "base_asset_id",
#         "base_asset_name",
#         "base_asset_flow",
#         "quote_asset_id",
#         "price",
#         "signed_gross_value",
#         "fee",
#         "quote_asset_flow",
#         "operation_type",
#     ]
# )

pl.Config.set_tbl_rows(-1)
pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_width_chars(200)
print(df)
