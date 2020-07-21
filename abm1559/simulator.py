from typing import Sequence, Dict

from abm1559.utils import (
    rng,
    constants,
)

from abm1559.txs import Transaction
from abm1559.chain import Block
from abm1559.users import User, User1559

def spawn_poisson_demand(timestep: int, demand_lambda: float) -> Sequence[User1559]:
    """
    Args:
        timestep (int): Current round
        demand_lambda (float): Rate of arrival, the :math:`lambda` parameter of a Poisson distribution

    Returns:
        Sequence[User1559]: An array of 1559 users
    """

    real = rng.poisson(demand_lambda)
    new_users = [User1559(timestep) for i in range(real)]
    return new_users

def decide_transactions(demand: Sequence[User], params: Dict) -> Sequence[Transaction]:
    """
    Queries all users and checks who wants to send transactions and who wants to balk.

    Args:
        demand (Sequence[User]): Current demand
        params (Dict): Current simulation environment parameters (e.g., basefee)

    Returns:
        Sequence[Transaction]: An array of transactions
    """

    txs = []
    basefee = params["basefee"]

    for user in demand:
        tx = user.transact({
            "basefee": basefee
        })
        if not tx is None:
            txs.append(tx)

    return txs

def update_basefee(block: Block, basefee: int) -> int:
    """
    Basefee update rule

    Args:
        block (Block): The previous block
        basefee (int): The current basefee

    Returns:
        int: The new basefee
    """

    gas_used = sum([tx.gas_used for tx in block.txs])
    delta = gas_used - constants["TARGET_GAS_USED"]
    return basefee + basefee * delta // constants["TARGET_GAS_USED"] // constants["BASEFEE_MAX_CHANGE_DENOMINATOR"]
