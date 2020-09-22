import abm1559.config
import numpy as np

constants = {
    "BASEFEE_MAX_CHANGE_DENOMINATOR": 8,
    "TARGET_GAS_USED": 10000000,
    "MAX_GAS_EIP1559": 20000000,
    "EIP1559_DECAY_RANGE": 800000,
    "EIP1559_GAS_INCREMENT_AMOUNT": 10,
    "INITIAL_BASEFEE": 1 * (10 ** 9),
    "PER_TX_GASLIMIT": 8000000,
    "SIMPLE_TRANSACTION_GAS": 21000,
}

def set_seed(seed):
    abm1559.config.rng = np.random.default_rng(seed)

def get_basefee_bounds(basefee, blocks):
    # We want to know how high/low the basefee can be after `blocks` steps, starting from `basefee`
    lb = basefee * (1 - 1.0 / constants["BASEFEE_MAX_CHANGE_DENOMINATOR"])
    ub = basefee * (1 + 1.0 / constants["BASEFEE_MAX_CHANGE_DENOMINATOR"])
    return { "lb": lb, "ub": ub }
