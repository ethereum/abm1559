from abm1559.utils import (
    rng,
    constants,
)

from abm1559.users import User1559

def spawn_demand(timestep, demand_lambda):
    real = rng.poisson(demand_lambda)
    new_users = [User1559(timestep) for i in range(real)]
    return new_users

def decide_transactions(demand, params):
    # User side
    txs = []
    basefee = params["basefee"]

    for user in demand:
        tx = user.transact({
            "basefee": basefee
        })
        if not tx is None:
            txs.append(tx)

    return txs

def select_transactions(txpool, params):
    # Miner side
    basefee = params["basefee"]
    max_tx_in_block = int(constants["MAX_GAS_EIP1559"] / constants["SIMPLE_TRANSACTION_GAS"])

    sorted_valid_demand = sorted(
        [tx for tx in txpool.txs.values() if tx.is_valid({ "basefee": basefee })],
        key = lambda tx: -tx.tip({ "basefee": basefee })
    )
    selected_txs = sorted_valid_demand[0:max_tx_in_block]

    return selected_txs

def update_basefee(block, basefee):
    gas_used = sum([tx.gas_used for tx in block.txs])
    delta = gas_used - constants["TARGET_GAS_USED"]
    return basefee + basefee * delta // constants["TARGET_GAS_USED"] // constants["BASEFEE_MAX_CHANGE_DENOMINATOR"]
