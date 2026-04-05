from pprint import pprint

import polars as pl

from finanzmaschine.catalog import asset_registry
from finanzmaschine.config import DATA_DIR_PATH
from finanzmaschine.portfolio.operation_types.trade_type import TradeType
from finanzmaschine.portfolio.records.base_record import Direction
from finanzmaschine.portfolio.records.crypto_etp_trade_record import CryptoEtpTradeRecord

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

    quote_asset = asset_registry.get(row["quote_asset_id"])
    price = row["price"]
    fee = row["fee"]

    broker = row["broker"]
    order_id = row["order_id"]
    exchange = row["exchange"]
    trade_id = row["trade_id"]

    record = CryptoEtpTradeRecord(
        quantity=quantity,
        datetime=datetime,
        direction=direction,
        operation_type=operation_type,
        quote_asset=quote_asset,
        price=price,
        fee=fee,
        broker=broker,
        order_id=order_id,
        exchange=exchange,
        trade_id=trade_id,
    )
    pprint(record)
