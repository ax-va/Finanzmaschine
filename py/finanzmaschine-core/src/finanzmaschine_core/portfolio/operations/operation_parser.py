from typing import Dict, NamedTuple

from finanzmaschine_core.portfolio.operations import TradeEnum, IncomeEnum

OperationEnum = IncomeEnum | TradeEnum

OPERATION_ENUM_BY_STR: Dict[str, type[OperationEnum]] = {
    "INCOME": IncomeEnum,
    "TRADE": TradeEnum,
}


class OperationNamedTuple(NamedTuple):
    type: type[OperationEnum]
    variant: OperationEnum


def parse_operation(operation_type_str: str, operation_variant_str: str) -> OperationNamedTuple:
    operation_type: type[OperationEnum] = OPERATION_ENUM_BY_STR[operation_type_str]
    operation_variant: OperationEnum = operation_type(operation_variant_str)
    return OperationNamedTuple(type=operation_type, variant=operation_variant)
