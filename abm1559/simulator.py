from typing import Sequence, Dict

from abm1559.utils import (
    rng,
    constants,
)

from abm1559.chain import Block
from abm1559.users import User, User1559

def spawn_users(timestep: int, demand_size: int, UserClass) -> Sequence[User]:
    return [UserClass(timestep) for i in range(demand_size)]

def spawn_poisson_demand(timestep: int, demand_lambda: float, UserClass) -> Sequence[User]:
    """
    One-step demand from homogeneous users, with demand size drawn from a Poisson distribution.

    Args:
        timestep (int): Current round
        demand_lambda (float): Rate of arrival, the :math:`lambda` parameter of a Poisson distribution
        UserClass (class): The user type

    Returns:
        Sequence[User]: An array of users
    """

    demand_size = rng.poisson(demand_lambda)
    new_users = spawn_users(timestep, demand_size, UserClass)
    return new_users

def spawn_poisson_heterogeneous_demand(timestep: int, demand_lambda: float, shares: Dict[type, float]) -> Sequence[User]:
    """
    One-step demand from heterogeneous users, with demand size drawn from a Poisson distribution.

    Args:
        timestep (int): Current round
        demand_lambda (float): Rate of arrival, the :math:`lambda` parameter of a Poisson distribution
        UserClass (Dict[type, float]): Keys are user classes (subclasses of :py:class:`abm1559.users.User`), values are the share of each user class to spawn this round. Shares are expected to sum to 1.

    Returns:
        Sequence[User]: An array of users
    """

    new_users = []
    demand_size = rng.poisson(demand_lambda)
    sizes = shares_to_sizes(shares, demand_size)
    for UserClass, size in sizes.items():
        new_users += [UserClass(timestep) for i in range(size)]
    return new_users

def shares_to_sizes(shares: Dict[type, float], demand_size: int) -> Dict[type, int]:
    new_sizes = {}
    for i, (UserClass, share) in enumerate(shares.items()):
        if i == len(shares.values()) - 1: # last item
            new_sizes[UserClass] = demand_size - sum(new_sizes.values())
        else:
            new_sizes[UserClass] = int(share * demand_size)
    return new_sizes

def update_basefee(block: Block, basefee: int, update_speed: int = constants["BASEFEE_MAX_CHANGE_DENOMINATOR"]) -> int:
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
    return basefee + basefee * delta // constants["TARGET_GAS_USED"] // update_speed
