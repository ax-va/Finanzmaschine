import re
from decimal import Decimal
from typing import TypeVar

import polars as pl
import pytest

from finanzmaschine.portfolio.positions.acquisition_position import AcquisitionPosition
from finanzmaschine.portfolio.positions.base_position import ClosingOrder
from finanzmaschine.utils.decimal_helper import round_to_quantum

P = TypeVar("P", bound="AcquisitionPosition")


@pytest.fixture(scope="function")
def position(request) -> P:
    return request.getfixturevalue(request.param)


@pytest.fixture(scope="function")
def df_golden_values(request) -> pl.DataFrame:
    return request.getfixturevalue(request.param)


@pytest.fixture(scope="function")
def df_transactions_sell(request) -> pl.DataFrame:
    return request.getfixturevalue(request.param)


@pytest.mark.parametrize(
    "position,"
    "df_golden_values,"
    "df_transactions_sell,"
    "expected_position_quantity_open,"
    "expected_position_quantity_closed,"
    "expected_position_proceeds,"
    "expected_position_cost_basis_sold,"
    "expected_position_pnl",
    [
        (
            "ton_etp_position_fifo_fifo",
            "df_expected_ton_etp_fifo_fifo",
            "df_ton_etp_sold",
            Decimal("109.459107"),
            Decimal("811"),
            Decimal("5065.52"),
            Decimal("5621.84"),
            Decimal("-556.32"),
        ),
        (
            "ton_etp_position_fifo_lifo",
            "df_expected_ton_etp_fifo_lifo",
            "df_ton_etp_sold",
            Decimal("109.459107"),
            Decimal("811"),
            Decimal("5065.52"),
            Decimal("5441.20"),
            Decimal("-375.68"),
        ),
        (
            "ton_etp_position_lifo_fifo",
            "df_expected_ton_etp_lifo_fifo",
            "df_ton_etp_sold",
            Decimal("109.459107"),
            Decimal("811"),
            Decimal("5065.52"),
            Decimal("5455.02"),
            Decimal("-389.50"),
        ),
        (
            "ton_etp_position_lifo_lifo",
            "df_expected_ton_etp_lifo_lifo",
            "df_ton_etp_sold",
            Decimal("109.459107"),
            Decimal("811"),
            Decimal("5065.52"),
            Decimal("5241.67"),
            Decimal("-176.15"),
        ),
    ],
    indirect=["position", "df_golden_values", "df_transactions_sell"],
)
def test_close_position(
    position: P,
    df_golden_values: pl.DataFrame,
    df_transactions_sell: pl.DataFrame,
    expected_position_quantity_open: Decimal,
    expected_position_quantity_closed: Decimal,
    expected_position_proceeds: Decimal,
    expected_position_cost_basis_sold: Decimal,
    expected_position_pnl: Decimal,
):
    # workaround for typechecker
    position: AcquisitionPosition

    # Set initial sell-values
    sell_index = 0
    base_asset_flow = Decimal(df_transactions_sell.row(sell_index, named=True)["base_asset_flow"])
    record_quantity_to_close = abs(base_asset_flow)
    record_fee_to_close = Decimal(df_transactions_sell.row(sell_index, named=True)["fee"])

    # Set initial lot values
    lot_values = {
        lot: {
            "lot_quantity_closed": Decimal("0"),
            "lot_proceeds": Decimal("0"),
            "lot_cost_basis_sold": Decimal("0"),
            "lot_pnl": Decimal("0"),
            "record_quantity_open_before": lot.record_in.quantity,
        } for lot in position.lots
    }

    for record_index, (record, lot) in enumerate(position.lot_by_record_sold.items()):

        record_quantity_open_before = lot_values[lot]["record_quantity_open_before"]

        # Test closing_order
        expected_record_closing_order = ClosingOrder(df_golden_values.row(record_index, named=True)["closing_order"])
        assert position.closing_order_by_record_out[record] == expected_record_closing_order

        # Test sell_id
        expected_sell_id = df_golden_values.row(record_index, named=True)["sell_id"]
        assert sell_index + 1 == int(re.search(r"\d+", expected_sell_id).group())
        expected_operation_type = df_transactions_sell.row(sell_index, named=True)["operation_type"]
        assert expected_operation_type in expected_sell_id

        # Test datetime_sold
        expected_record_datetime_sold = df_golden_values.row(record_index, named=True)["datetime_sold"]
        assert df_transactions_sell.row(sell_index, named=True)["datetime"] == expected_record_datetime_sold

        # Test lot_id
        expected_lot_id = df_golden_values.row(record_index, named=True)["lot_id"]
        assert position.get_lot_id(lot) == expected_lot_id

        # Test datetime_open
        expected_record_datetime_open = df_golden_values.row(record_index, named=True)["datetime_open"]
        assert lot.record_in.datetime == expected_record_datetime_open

        # Test quantity_open_before
        expected_record_quantity_open_before = Decimal(df_golden_values.row(record_index, named=True)["quantity_open_before"])
        assert record_quantity_open_before == expected_record_quantity_open_before

        # Test quantity_to_close
        expected_record_quantity_to_close = Decimal(df_golden_values.row(record_index, named=True)["quantity_to_close"])
        assert record_quantity_to_close == expected_record_quantity_to_close

        # Test quantity_closed
        expected_record_quantity_closed = Decimal(df_golden_values.row(record_index, named=True)["quantity_closed"])
        assert record.quantity == expected_record_quantity_closed
        record_quantity_open_after = record_quantity_open_before - expected_record_quantity_closed

        # Test quantity_open_after
        expected_record_quantity_open_after = Decimal(df_golden_values.row(record_index, named=True)["quantity_open_after"])
        assert record_quantity_open_after == expected_record_quantity_open_after

        # Test quantity_remaining
        expected_record_quantity_remaining = Decimal(df_golden_values.row(record_index, named=True)["quantity_remaining"])
        record_quantity_remaining = record_quantity_to_close - record.quantity
        assert record_quantity_remaining == expected_record_quantity_remaining

        # Test fee_to_closed
        expected_record_fee_to_close = Decimal(df_golden_values.row(record_index, named=True)["fee_to_close"])
        assert record_fee_to_close == expected_record_fee_to_close

        # Test fee_closed
        expected_record_fee_closed = Decimal(df_golden_values.row(record_index, named=True)["fee_closed"])
        assert record.fee.get_total(lot.single_quote_asset) == expected_record_fee_closed

        # Test fee_remaining
        expected_record_fee_remaining = Decimal(df_golden_values.row(record_index, named=True)["fee_remaining"])
        record_fee_remaining = record_fee_to_close - record.fee.get_total(lot.single_quote_asset)
        assert record_fee_remaining == expected_record_fee_remaining

        # Test proceeds
        expected_record_proceeds = Decimal(df_golden_values.row(record_index, named=True)["proceeds"])
        record_proceeds = round_to_quantum(
            record.quantity * record.price - record.fee.get_total(lot.single_quote_asset),
            lot.record_in.quote_asset.quantum,
        )
        assert record_proceeds == expected_record_proceeds

        # Test cost_basis_sold
        expected_record_cost_basis_sold = Decimal(df_golden_values.row(record_index, named=True)["cost_basis_sold"])
        record_cost_basis_sold = round_to_quantum(
            record.quantity / lot.record_in.quantity * lot.cost_basis,
            lot.record_in.quote_asset.quantum,
        )
        assert record_cost_basis_sold == expected_record_cost_basis_sold

        # Test pnl
        expected_record_pnl = Decimal(df_golden_values.row(record_index, named=True)["pnl"])
        record_pnl = record_proceeds - record_cost_basis_sold
        assert record_pnl == expected_record_pnl

        # Update values
        record_quantity_to_close = record_quantity_remaining
        record_fee_to_close = record_fee_remaining
        if record_quantity_to_close == Decimal("0"):
            sell_index += 1
            if sell_index < len(df_transactions_sell):
                base_asset_flow = Decimal(df_transactions_sell.row(sell_index, named=True)["base_asset_flow"])
                record_quantity_to_close = abs(base_asset_flow)
                record_fee_to_close = Decimal(df_transactions_sell.row(sell_index, named=True)["fee"])

        lot_values[lot]["record_quantity_open_before"] = record_quantity_open_after
        lot_values[lot]["lot_quantity_closed"] += record.quantity
        lot_values[lot]["lot_proceeds"] += record_proceeds
        lot_values[lot]["lot_cost_basis_sold"] += record_cost_basis_sold
        lot_values[lot]["lot_pnl"] += record_pnl

    # Test position attributes
    assert position.quantity_open == expected_position_quantity_open
    assert position.quantity_closed == expected_position_quantity_closed
    assert position.proceeds == expected_position_proceeds
    assert position.cost_basis_sold == expected_position_cost_basis_sold
    assert position.pnl == expected_position_pnl

    # Set initial position values to test through lots
    position_proceeds = Decimal("0")
    position_cost_basis_sold = Decimal("0")
    position_pnl = Decimal("0")

    for lot in position.lots:

        # Test lot attributes
        assert lot.quantity_open == lot_values[lot]["record_quantity_open_before"]
        assert lot.quantity_closed == lot_values[lot]["lot_quantity_closed"]
        assert lot.proceeds == lot_values[lot]["lot_proceeds"]
        assert lot.cost_basis_sold == lot_values[lot]["lot_cost_basis_sold"]
        assert lot.pnl == lot_values[lot]["lot_pnl"]

        position_proceeds += lot.proceeds
        position_cost_basis_sold += lot.cost_basis_sold
        position_pnl += lot.pnl

    # Test position attributes through lots
    assert position.proceeds == position_proceeds
    assert position.cost_basis_sold == position_cost_basis_sold
    assert position.pnl == position_pnl
