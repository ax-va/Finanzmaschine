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
def golden_values(request) -> pl.DataFrame:
    return request.getfixturevalue(request.param)


@pytest.fixture(scope="function")
def transactions_sell(request) -> pl.DataFrame:
    return request.getfixturevalue(request.param)


@pytest.mark.parametrize(
    "position,golden_values,transactions_sell,quantity_open_total,quantity_closed_total,proceeds_total,cost_basis_sold_total,pnl_total",
    [
        ("ton_etp_position_fifo", "df_ton_etp_fifo", "df_ton_etp_sold", Decimal("109.459107"), Decimal("811"), Decimal("5065.52"), Decimal("5621.84"), Decimal("-556.32")),
    ],
    indirect=["position", "golden_values", "transactions_sell"],
)
def test_close_position(
        position: P,
        golden_values: pl.DataFrame,
        transactions_sell: pl.DataFrame,
        quantity_open_total: Decimal,
        quantity_closed_total: Decimal,
        proceeds_total: Decimal,
        cost_basis_sold_total: Decimal,
        pnl_total: Decimal,
):
    # workaround for typechecker
    position: AcquisitionPosition

    position_proceeds = Decimal("0")
    position_cost_basis_sold = Decimal("0")
    position_pnl = Decimal("0")

    sell_idx = 0
    base_asset_flow = Decimal(transactions_sell.row(sell_idx, named=True)["base_asset_flow"])
    record_quantity_to_close = abs(base_asset_flow)
    record_fee_to_close = Decimal(transactions_sell.row(sell_idx, named=True)["fee"])

    record_idx = 0
    for lot in position.lots_with_records_sold:

        lot_quantity_closed = Decimal("0")
        lot_proceeds = Decimal("0")
        lot_cost_basis_sold = Decimal("0")
        lot_pnl = Decimal("0")

        record_quantity_open_before = lot.record_in.quantity

        for record in lot.records_sold:

            # Test closing_order
            closing_order = ClosingOrder(golden_values.row(record_idx, named=True)["closing_order"])
            assert position.closing_orders[record] == closing_order

            # Test datetime_open
            datetime_open = golden_values.row(record_idx, named=True)["datetime_open"]
            assert lot.record_in.datetime == datetime_open

            # Test datetime_sold
            datetime_sold = golden_values.row(record_idx, named=True)["datetime_sold"]
            assert transactions_sell.row(sell_idx, named=True)["datetime"] == datetime_sold

            # Test quantity_open_before
            assert record_quantity_open_before == Decimal(golden_values.row(record_idx, named=True)["quantity_open_before"])

            # Test quantity_to_close
            assert record_quantity_to_close == Decimal(golden_values.row(record_idx, named=True)["quantity_to_close"])

            # Test quantity_closed
            record_quantity_closed = Decimal(golden_values.row(record_idx, named=True)["quantity_closed"])
            assert record.quantity == record_quantity_closed
            record_quantity_open_after = record_quantity_open_before - record_quantity_closed

            # Test quantity_open_after
            assert record_quantity_open_after == Decimal(golden_values.row(record_idx, named=True)["quantity_open_after"])

            # Test quantity_remaining
            record_quantity_remaining = record_quantity_to_close - record.quantity
            assert record_quantity_remaining == Decimal(golden_values.row(record_idx, named=True)["quantity_remaining"])

            # Test fee_to_closed
            assert record_fee_to_close == Decimal(golden_values.row(record_idx, named=True)["fee_to_close"])

            # Test fee_closed
            assert record.fee == Decimal(golden_values.row(record_idx, named=True)["fee_closed"])

            # Test fee_remaining
            record_fee_remaining = record_fee_to_close - record.fee
            assert record_fee_remaining == Decimal(golden_values.row(record_idx, named=True)["fee_remaining"])

            # Test proceeds
            record_proceeds = round_to_quantum(
                record.quantity * record.price - record.fee,
                lot.record_in.quote_asset.quantum,
            )
            assert record_proceeds == Decimal(golden_values.row(record_idx, named=True)["proceeds"])

            # Test cost_basis_sold
            record_cost_basis_sold = round_to_quantum(
                record.quantity / lot.record_in.quantity * lot.cost_basis,
                lot.record_in.quote_asset.quantum,
            )
            assert record_cost_basis_sold == Decimal(golden_values.row(record_idx, named=True)["cost_basis_sold"])

            # Test pnl
            record_pnl = record_proceeds - record_cost_basis_sold
            assert record_pnl == Decimal(golden_values.row(record_idx, named=True)["pnl"])

            record_quantity_to_close = record_quantity_remaining
            record_fee_to_close = record_fee_remaining
            if record_quantity_to_close == Decimal("0"):
                sell_idx += 1
                if sell_idx < len(transactions_sell):
                    base_asset_flow = Decimal(transactions_sell.row(sell_idx, named=True)["base_asset_flow"])
                    record_quantity_to_close = abs(base_asset_flow)
                    record_fee_to_close = Decimal(transactions_sell.row(sell_idx, named=True)["fee"])

            record_quantity_open_before = record_quantity_open_after

            lot_quantity_closed += record.quantity
            lot_proceeds += record_proceeds
            lot_cost_basis_sold += record_cost_basis_sold
            lot_pnl += record_pnl

            record_idx += 1

        # Test lot attributes
        assert lot.quantity_closed == lot_quantity_closed
        assert lot.proceeds == lot_proceeds
        assert lot.cost_basis_sold == lot_cost_basis_sold
        assert lot.pnl == lot_pnl

        position_proceeds += lot_proceeds
        position_cost_basis_sold += lot_cost_basis_sold
        position_pnl += lot_pnl

    # Test position attributes
    assert position.quantity_open == quantity_open_total
    assert position.quantity_closed == quantity_closed_total
    assert position.proceeds == proceeds_total
    assert position.cost_basis_sold == cost_basis_sold_total
    assert position.pnl == pnl_total

    assert position.proceeds == position_proceeds
    assert position.cost_basis_sold == position_cost_basis_sold
    assert position.pnl == position_pnl
