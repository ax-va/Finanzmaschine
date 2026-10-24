import polars as pl

from fzm_near.helpers import constants as const

BALANCE_SCHEMA = {
    const.BLOCK_HEIGHT: pl.Int64,
    const.STAKED_YOCTO_STR: pl.String,
    const.UNSTAKED_YOCTO_STR: pl.String,
}

SNAPSHOT_SCHEMA = {
    const.ACCOUNT_KEY: pl.String,
    const.POOL_KEY: pl.String,
    **BALANCE_SCHEMA,
}

SEARCH_INTERVAL_SCHEMA = {
    const.POOL_KEY: pl.String,
    const.FROM_BLOCK_HEIGHT: pl.Int64,
    const.UP_TO_BLOCK_HEIGHT: pl.Int64,
}

FINAL_STATE_SCHEMA = {
    const.POOL_KEY: pl.String,
    const.IS_ACTIVE: pl.Boolean,
}

ACTION_SCHEMA = {
    const.RECEIPT_KEY: pl.String,
    const.ACTION_INDEX: pl.Int64,
    const.ACCOUNT_KEY: pl.String,
    const.POOL_KEY: pl.String,
    const.EXEC_OUTCOME_BLOCK_HEIGHT: pl.Int64,
    const.EXEC_OUTCOME_INDEX: pl.Int64,
    const.METHOD_NAME: pl.String,
    const.OPERATION_YOCTO_STR: pl.String,
}