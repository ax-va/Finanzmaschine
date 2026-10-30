from fzm_near.orm.staking.balance import Balance


def get_balance(block_height: int) -> Balance:
    staked_yocto = 100 + (block_height // 100)

    return Balance(
        block_height=block_height,
        staked_yocto_str=str(staked_yocto),
        unstaked_yocto_str="2",
    )


def is_missing_block(block_height: int) -> bool:
    return block_height % 7 == 0 or block_height % 13 == 0
