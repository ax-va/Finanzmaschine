import re
from decimal import Decimal
from typing import TypeVar

import polars as pl
import pytest

from finanzmaschine.portfolio.positions.acquisition_position import AcquisitionPosition
from finanzmaschine.utils.decimal_helper import round_to_quantum

P = TypeVar("P", bound="AcquisitionPosition")


@pytest.fixture(scope="function")
def position(request) -> P:
    return request.getfixturevalue(request.param)


@pytest.fixture(scope="function")
def golden_values(request) -> pl.DataFrame:
    return request.getfixturevalue(request.param)


@pytest.mark.parametrize(
    "position,golden_values,num_lots,quantity_open,quantity_closed,proceeds,cost_basis_sold,pnl",
    [
        ("ton_etp_position_fifo", "df_ton_etp_fifo", 14, Decimal("109.459107"), Decimal("811"), Decimal("5065.52"), Decimal("5621.84"), Decimal("-556.32")),
    ],
    indirect=["position", "golden_values"],
)
def test_close_position(
        position: P,
        golden_values: pl.DataFrame,
        num_lots: int,
        quantity_open: Decimal,
        quantity_closed: Decimal,
        proceeds: Decimal,
        cost_basis_sold: Decimal,
        pnl: Decimal,
):
    # workaround for typechecker
    position: AcquisitionPosition

    position_proceeds = Decimal("0")
    position_cost_basis_sold = Decimal("0")
    position_pnl = Decimal("0")

    i_record = 0
    for lot in position.lots_with_records_sold:

        lot_quantity_closed = Decimal("0")
        lot_proceeds = Decimal("0")
        lot_cost_basis_sold = Decimal("0")
        lot_pnl = Decimal("0")

        for record in lot.records_sold:
            assert record.quantity == Decimal(golden_values.row(i_record, named=True)["quantity_closed"])
            assert record.fee == Decimal(golden_values.row(i_record, named=True)["fee_closed"])

            record_proceeds = round_to_quantum(
                record.quantity * record.price - record.fee,
                lot.record_in.quote_asset.quantum,
            )
            assert record_proceeds == Decimal(golden_values.row(i_record, named=True)["proceeds"])

            record_cost_basis_sold = round_to_quantum(
                record.quantity / lot.record_in.quantity * lot.cost_basis,
                lot.record_in.quote_asset.quantum,
            )
            assert record_cost_basis_sold == Decimal(golden_values.row(i_record, named=True)["cost_basis_sold"])

            record_pnl = record_proceeds - record_cost_basis_sold
            assert record_pnl == Decimal(golden_values.row(i_record, named=True)["pnl"])

            lot_quantity_closed += record.quantity
            lot_proceeds += record_proceeds
            lot_cost_basis_sold += record_cost_basis_sold
            lot_pnl += record_pnl

            i_record += 1

        assert lot.quantity_closed == lot_quantity_closed
        assert lot.proceeds == lot_proceeds
        assert lot.cost_basis_sold == lot_cost_basis_sold
        assert lot.pnl == lot_pnl

        position_proceeds += lot_proceeds
        position_cost_basis_sold += lot_cost_basis_sold
        position_pnl += lot_pnl

    assert len(position.lots_with_records_sold) == num_lots
    assert position.quantity_open == quantity_open
    assert position.quantity_closed == quantity_closed
    assert position.proceeds == proceeds
    assert position.cost_basis_sold == cost_basis_sold
    assert position.pnl == pnl

    assert position.proceeds == position_proceeds
    assert position.cost_basis_sold == position_cost_basis_sold
    assert position.pnl == position_pnl
