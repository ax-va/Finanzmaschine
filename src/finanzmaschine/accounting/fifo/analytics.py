import polars as pl

from finanzmaschine import PROJECT_ROOT
from finanzmaschine.config import SETTINGS

PRIVATE_DIR = PROJECT_ROOT / SETTINGS.paths.private

df = (
    pl.read_csv(
        PRIVATE_DIR / "etp_ton.csv",
        try_parse_dates=True,
    ).sort("datetime")
)

df = (
    df.with_columns(
        (pl.col("units") * pl.col("price")).round(2).alias("notional"),
    )
    .select([
        "datetime",
        "broker",
        "venue",
        "order_id",
        "trade_id",
        "isin",
        "instrument",
        "units",
        "price",
        "notional",
        "fee",
        "total",
        "currency",
        "side",
    ])
)
pl.Config.set_tbl_rows(-1)
pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_width_chars(200)
print(df)