from typing import Sequence, Dict

from abm1559.utils import (
    rng,
    constants,
)

from abm1559.txs import Transaction
from abm1559.chain import Block
from abm1559.users import User, User1559

def spawn_poisson_demand(timestep: int, demand_lambda: float, UserClass) -> Sequence[User]:
    """
    One-step demand from uniform users, with demand size drawn from a Poisson distribution.

    Args:
        timestep (int): Current round
        demand_lambda (float): Rate of arrival, the :math:`lambda` parameter of a Poisson distribution
        UserClass (class): The user type

    Returns:
        Sequence[User]: An array of users
    """

    demand_size = rng.poisson(demand_lambda)
    new_users = [UserClass(timestep) for i in range(demand_size)]
    return new_users

def spawn_poisson_heterogeneous_demand(timestep: int, demand_lambda: float, shares: Dict) -> Sequence[User]:
    """

    """

    new_users = []
    demand_size = rng.poisson(demand_lambda)
    sizes = shares_to_sizes(shares, demand_size)
    for UserClass, size in sizes.items():
        new_users += [UserClass(timestep) for i in range(size)]
    return new_users

def shares_to_sizes(shares: Dict, demand_size: int) -> Dict:
    new_sizes = {}
    for i, (UserClass, share) in enumerate(shares.items()):
        if i == len(shares.values()) - 1: # last item
            new_sizes[UserClass] = demand_size - sum(new_sizes.values())
        else:
            new_sizes[UserClass] = int(share * demand_size)
    return new_sizes

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

    for user in demand:
        tx = user.transact(params)
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
