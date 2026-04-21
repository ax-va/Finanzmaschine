from decimal import Decimal

import polars as pl

from finanzmaschine.catalog import asset_registry
from finanzmaschine.portfolio.assets import CryptoEtp
from finanzmaschine.portfolio.operation_types import TradeType
from finanzmaschine.portfolio.positions import CryptoEtpPosition
from finanzmaschine.portfolio.records import Direction
from finanzmaschine.portfolio.records import CryptoEtpTradeRecord
from finanzmaschine.utils.decimal_helper import round_to_quantum


def test_ton_etp_fifo_closing(data_dir):

    df_fifo = pl.read_csv(data_dir / "etps/toncoin_fifo_closing.csv",
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

    df_trades = pl.read_csv(data_dir / "etps/toncoin.csv",
        try_parse_dates=True,
        schema_overrides={
            "price": pl.String,
            "fee": pl.String,
            "base_asset_flow": pl.String,
            "quote_asset_flow": pl.String,
        },
    ).sort("datetime")

    base_asset: CryptoEtp = asset_registry.get("CH1297762812")
    position = CryptoEtpPosition(base_asset=base_asset)

    for row in df_trades.iter_rows(named=True):
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

    i = 0
    for lot in position.lots_with_records_sold:

        lot_proceeds = Decimal("0")
        lot_cost_basis_sold = Decimal("0")
        lot_pnl = Decimal("0")

        for record in lot.records_sold:
            assert record.quantity ==  Decimal(df_fifo.row(i, named=True)["quantity_closed"])
            assert record.fee == Decimal(df_fifo.row(i, named=True)["fee_closed"])

            record_proceeds = round_to_quantum(
                record.quantity * record.price - record.fee,
                lot.record_in.quote_asset.quantum,
            )
            assert record_proceeds == Decimal(df_fifo.row(i, named=True)["proceeds"])

            record_cost_basis_sold = round_to_quantum(
                record.quantity / lot.record_in.quantity * lot.cost_basis,
                lot.record_in.quote_asset.quantum,
            )
            assert record_cost_basis_sold == Decimal(df_fifo.row(i, named=True)["cost_basis_sold"])

            record_pnl = record_proceeds - record_cost_basis_sold
            assert record_pnl == Decimal(df_fifo.row(i, named=True)["pnl"])

            lot_proceeds += Decimal(df_fifo.row(i, named=True)["proceeds"])
            lot_cost_basis_sold += Decimal(df_fifo.row(i, named=True)["cost_basis_sold"])
            lot_pnl += Decimal(df_fifo.row(i, named=True)["pnl"])

            i += 1

        assert lot.proceeds == lot_proceeds
        assert lot.cost_basis_sold == lot_cost_basis_sold
        assert lot.pnl == lot_pnl
