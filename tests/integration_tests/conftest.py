from decimal import Decimal

import polars as pl
import pytest

from finanzmaschine.catalog import asset_registry
from finanzmaschine.portfolio.assets import CryptoEtp
from finanzmaschine.portfolio.operation_types import TradeType
from finanzmaschine.portfolio.positions import CryptoEtpPosition
from finanzmaschine.portfolio.records import Direction, CryptoEtpTradeRecord


@pytest.fixture(scope="session")
def df_ton_etp_fifo(data_dir) -> pl.DataFrame:
    df = pl.read_csv(data_dir / "etps/ton_etp_fifo.csv",
        try_parse_dates=True,
        schema_overrides={
          "quantity_open_before": pl.String,
          "quantity_to_close": pl.String,
          "quantity_open_after": pl.String,
          "quantity_closed": pl.String,
          "quantity_remaining": pl.String,
          "fee_to_close": pl.String,
          "fee_closed": pl.String,
          "fee_remaining": pl.String,
          "proceeds": pl.String,
          "cost_basis_sold": pl.String,
          "pnl": pl.String,
        },
    )
    return df


@pytest.fixture(scope="session")
def df_ton_etp_trade(data_dir) -> pl.DataFrame:
    df = pl.read_csv(data_dir / "etps/ton_etp_trade.csv",
        try_parse_dates=True,
        schema_overrides={
            "price": pl.String,
            "fee": pl.String,
            "base_asset_flow": pl.String,
            "quote_asset_flow": pl.String,
        },
    ).sort("datetime")
    return df


@pytest.fixture(scope="session")
def df_ton_etp_sold(df_ton_etp_trade) -> pl.DataFrame:
    return df_ton_etp_trade.filter(pl.col("operation_type") == TradeType.SELL)


@pytest.fixture(scope="session")
def ton_etp_position_fifo(df_ton_etp_trade) -> CryptoEtpPosition:
    base_asset: CryptoEtp = asset_registry.get("CH1297762812")
    position = CryptoEtpPosition(base_asset=base_asset)

    for row in df_ton_etp_trade.iter_rows(named=True):
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
        position.apply(record, "FIFO")

    return position