from decimal import Decimal
from pprint import pprint

import polars as pl

from finanzmaschine.catalog import asset_registry
from finanzmaschine.config import DATA_DIR_PATH
from finanzmaschine.portfolio.assets import CryptoEtp
from finanzmaschine.portfolio.operation_types import TradeType
from finanzmaschine.portfolio.positions import CryptoEtpPosition
from finanzmaschine.portfolio.positions.base_position import ClosingOrder
from finanzmaschine.portfolio.records import Direction
from finanzmaschine.portfolio.records import CryptoEtpTradeRecord

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

ton_etp: CryptoEtp = asset_registry.get("CH1297762812")
position = CryptoEtpPosition(base_asset=ton_etp)
position.closing_order = ClosingOrder.LIFO

for row in df.iter_rows(named=True):
    base_asset_flow = row["base_asset_flow"]
    quantity = abs(Decimal(base_asset_flow))
    datetime = row["datetime"]
    direction = Direction.OUT if base_asset_flow.startswith("-") else Direction.IN
    operation_type = TradeType(row["operation_type"])

    quote_asset = asset_registry.get(row["quote_asset_id"])
    price = Decimal(row["price"])
    fee = Decimal(row["fee"])

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
    position.apply(record)
    # print("Quantity open:", position.quantity_open)
    # print("Quantity closed:", position.quantity_closed)

for lot in position.lots_with_records_sold:
    print("Proceeds:", lot.proceeds)
    print("Cost basis sold:", lot.cost_basis_sold)
    print("PnL:", lot.pnl)
    for record_out in lot.records_sold:
        pprint(record_out)

print("Quantity closed:", position.quantity_closed)
print("Quantity open:", position.quantity_open)
print("PnL (N+1):", position.pnl)
print("Proceeds:", position.proceeds)
print("Cost basis sold:", position.cost_basis_sold)
