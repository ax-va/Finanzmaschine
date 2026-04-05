import polars as pl

from finanzmaschine.config import DATA_DIR_PATH
from finanzmaschine.portfolio.operation_types.trade_type import TradeType
from finanzmaschine.portfolio.records.base_record import Direction

df = pl.read_csv(
    DATA_DIR_PATH / "private" / "trades" / "etps" / "toncoin.csv",
    try_parse_dates=True,
).sort("datetime")

for row in df.iter_rows(named=True):
    base_asset_flow = row["base_asset_flow"]
    quantity = abs(base_asset_flow)
    datetime = row["datetime"]
    direction = Direction.IN if base_asset_flow > 0 else Direction.OUT
    operation_type = TradeType(row["operation_type"])
    broker = row["broker"]
