from abm1559.utils import constants

from abm1559.txpool import TxPool

from abm1559.chain import (
    Chain,
    Block1559,
)

from abm1559.simulator import (
    spawn_demand,
    decide_transactions,
    select_transactions,
    update_basefee,
)

import pd

txpool = TxPool()
basefee = constants["INITIAL_BASEFEE"]
chain = Chain()
metrics = []

for t in range(200):
    if t % 100 == 0: print(t)
    params = {
        "basefee": basefee,
        "current_block": t,
    }
    users = spawn_demand(t, 1000)
    decided_txs = decide_transactions(users, {
        "basefee": basefee,
        "current_block": t,
    })
    txpool.add_txs(decided_txs)
    txpool.select_transactions({
        "basefee": basefee,
        "current_block": t,
    })
    block = Block1559(txs = selected_txs, parent_hash = chain.current_head, height = t, basefee = basefee)
    txpool.remove_txs([tx.tx_hash for tx in selected_txs])
    chain.add_block(block)

    row_metrics = {
        "timestep": t,
        "basefee": basefee / (10 ** 9),
        "users": len(users),
        "decided_txs": len(decided_txs),
        "included_txs": len(selected_txs),
        "blk_avg_gas_price": block.average_gas_price(),
        "blk_avg_tip": block.average_tip(),
        "blk_avg_waiting_time": block.average_waiting_time(),
        "pool_length": txpool.pool_length,
        "pool_avg_tip": txpool.average_tip(params),
    }
    metrics.append(row_metrics)

    basefee = update_basefee(block, basefee)

df = pd.DataFrame(metrics)
