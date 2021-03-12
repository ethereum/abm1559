import numpy as np

constants = {
    "BASEFEE_MAX_CHANGE_DENOMINATOR": 8,
    "TARGET_GAS_USED": 12500000,
    "MAX_GAS_EIP1559": 25000000,
    "EIP1559_DECAY_RANGE": 800000,
    "EIP1559_GAS_INCREMENT_AMOUNT": 10,
    "INITIAL_BASEFEE": 1 * (10 ** 9),
    "PER_TX_GASLIMIT": 8000000,
    "SIMPLE_TRANSACTION_GAS": 21000,
}

def get_basefee_bounds(basefee, blocks):
    # We want to know how high/low the basefee can be after `blocks` steps, starting from `basefee`
    lb = basefee * ((1 - 1.0 / constants["BASEFEE_MAX_CHANGE_DENOMINATOR"]) ** blocks)
    ub = basefee * ((1 + 1.0 / constants["BASEFEE_MAX_CHANGE_DENOMINATOR"]) ** blocks)
    return { "lb": lb, "ub": ub }

flatten = lambda l: [item for sublist in l for item in sublist]

def basefee_from_csv_history(initial_basefee, csv_path):
    import pandas as pd
    from collections import defaultdict
    from abm1559.simulator import update_basefee

    df = pd.read_csv(csv_path, sep=",")
    txs = df.to_dict('records')
    blocks_list = defaultdict(list)
    class Tx():
        def __init__(self, gas_used, gas_price):
            self.gas_used = gas_used
            self.gas_price = gas_price
    class Block(dict):
        def __init__(self, txs):
            self.txs = txs

    for tx in txs:
        # gwei to wei
        gas_price = tx["gas_price"] * (10 ** 9)
        new_tx = Tx(tx["gas_used"], gas_price)
        blocks_list[tx["block_number"]].append(new_tx)

    base_fee = initial_basefee
    for block_num, curr_list in blocks_list.items():
        curr_block = Block(curr_list)
        filtered = [tx for tx in curr_block.txs if tx.gas_price > base_fee]
        base_fee = update_basefee(Block(filtered), base_fee)

    return base_fee
