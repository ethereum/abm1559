from typing import Sequence, Dict
import numpy as np

from abm1559.config import rng

from abm1559.utils import (
    constants,
)

from abm1559.chain import Block
from abm1559.users import User, User1559

def spawn_poisson_demand(timestep: int, demand_lambda: float, UserClass, rng: np.random.Generator = rng) -> Sequence[User]:
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
    new_users = [UserClass(timestep, rng=rng) for i in range(demand_size)]
    return new_users

def spawn_poisson_heterogeneous_demand(timestep: int, demand_lambda: float, shares: Dict[type, float], rng: np.random.Generator = rng) -> Sequence[User]:
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
        new_users += [UserClass(timestep, rng=rng) for i in range(size)]
    return new_users

def shares_to_sizes(shares: Dict[type, float], demand_size: int) -> Dict[type, int]:
    new_sizes = {}
    for i, (UserClass, share) in enumerate(shares.items()):
        if i == len(shares.values()) - 1: # last item
            new_sizes[UserClass] = demand_size - sum(new_sizes.values())
        else:
            new_sizes[UserClass] = int(share * demand_size)
    return new_sizes

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
    if gas_used == constants["TARGET_GAS_USED"]:
        new_basefee = basefee
    elif gas_used > constants["TARGET_GAS_USED"]:
        gas_delta = gas_used - constants["TARGET_GAS_USED"]
        fee_delta = max(basefee * gas_delta // constants["TARGET_GAS_USED"] // constants["BASEFEE_MAX_CHANGE_DENOMINATOR"], 1)
        new_basefee = basefee + fee_delta
    else:
        gas_delta = constants["TARGET_GAS_USED"] - gas_used
        fee_delta = basefee * gas_delta // constants["TARGET_GAS_USED"] // constants["BASEFEE_MAX_CHANGE_DENOMINATOR"]
        new_basefee = basefee - fee_delta
    return new_basefee

def generate_seeds(seeds: int = 100, rng: np.random.Generator = rng):
    return rng.integers(low=0, high=seeds*1000, size=seeds)

def generate_gbm(lambda_0: float, T: int, paths: int = 1, mu: float = 0.5, sigma: float = 1, rng: np.random.Generator = rng):
    t = np.repeat(np.array([np.arange(1, T+1)]), paths, axis = 0)
    b = rng.normal(size=[paths, T])
    w = b.cumsum(axis = 1)
    drift = (mu - 0.5 * sigma**2) * t
    diffusion = sigma * w
    S = lambda_0 * np.exp(drift + diffusion)
    return S

def apply_block_time_variance(demand_process: Sequence[float], blocks: int, mean_ia_time: float = 13, rng: np.random.Generator = rng) -> Sequence[int]:
    # Block time differences are distributed along a Poisson(13)
    ia_times = rng.exponential(13, blocks)
    demand_per_block = []
    current_time = 0
    for block_index, ia_time in enumerate(ia_times):
        ia_time = int(ia_time)
        new_demand = 0
        for t in range(current_time, current_time + ia_time):
            new_demand += demand_process[t]
        demand_per_block += [int(new_demand)]
        current_time += ia_time
    return demand_per_block