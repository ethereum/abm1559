from typing import Dict

import pandas as pd

from abm1559.utils import (
    get_basefee_bounds,
    rng
)

from abm1559.txs import Tx1559

class User:
    """
    Users submit transactions. They have a (randomly chosen) value per Gwei $v$, (we choose per Gwei such that all evaluations of their welfare can be done independently of how much gas the transaction uses).

    The user evaluates the total cost of the transaction in one of two ways, embodied by two different subclasses:

    - :py:class:`abm1559.users.AffineUser`: Incurs a fixed (but randomly selected) cost :math:`c` per unit of time (block-to-block), so :math:`cost(t) = v - c * t`.
    - :py:class:`abm1559.users.DiscountUser`: Incurs a discount :math:`\delta` over time, so :math:`cost(t) = v * (1 - \delta)^t`.

    `AffineUser` or `DiscountUser` are subclassed to create users who send different types of transactions, e.g., 1559-type transactions, escalators or something different. The subclasses should implement:

    - (Optional) `expected_time(params)`: How the user estimates how long they will wait for their transaction to be included.
    - (Optional) `decide_parameters(params)`: Based on their type and `params` (typically, current basefee, length of the queue or salient statistics e.g., distribution of tips in the queue), return transaction parameters.
    - (Requested) `transact(params)`: Queried by the simulation when user is spawned. Returns either a transaction or `None` if they balk.
    """

    def __init__(self, wakeup_block):
        self.pub_key = rng.bytes(8)
        self.wakeup_block = wakeup_block

        # Users have a value (in wei) per unit of gas for the transaction
        self.value = int(rng.uniform(low = 0, high = 20) * (10 ** 9))

    def payoff(self, params):
        """
        Args:
            params (Dict): Includes `gas_price` in wei
        """
        gas_price = params["gas_price"]
        return self.cost(params) - gas_price

    def export(self):
        return {
            "user": self,
            "pub_key": self.pub_key,
            "value": self.value,
        }

class AffineUser(User):
    """
    Affine users incur a fixed cost per unit of time.
    """

    def __init__(self, wakeup_block):
        super().__init__(wakeup_block)
        self.cost_per_unit = int(rng.uniform(low = 0, high = 1) * (10 ** 9))

    def __str__(self):
        return f"Affine User with value {self.value} and cost {self.cost_per_unit}"

    def cost(self, params):
        current_block = params["current_block"]
        elapsed_time = current_block - self.wakeup_block
        return self.value - self.cost_per_unit * elapsed_time

    def export(self):
        return {
            "user_type": "affine_user",
            "cost_per_unit": self.cost_per_unit,
            **super().export(),
        }

class DiscountUser(User):
    """
    The value of discount users is reduced over time.
    """

    def __init__(self, wakeup_block):
        super().__init__(wakeup_block)
        self.discount_rate = 0.01

    def __str__(self):
        return f"Discount User with value {self.value} and discount rate {self.discount_rate}"

    def cost(self, params):
        current_block = params["current_block"]
        elapsed_time = current_block - self.wakeup_block
        return self.value * (1 - self.discount_rate) ** elapsed_time

    def export(self):
        return {
            "user_type": "discount_user",
            "discount_rate": self.discount_rate,
            **super().export(),
        }

class User1559(AffineUser):
    """
    An affine user sending 1559 transactions.
    """
    # Expects to be included within 5 blocks
    # Prefers not to participate if its expected payoff is negative
    # Computes expected payoff by estimating the worst possible basefee 5 blocks from now
    # Fixed gas_premium

    def expected_time(self, params):
        return 5

    def decide_parameters(self):
        gas_premium = 1 * (10 ** 9)
        # max_fee = self.value - self.expected_time(params = {}) * self.cost_per_unit
        max_fee = self.value
        return {
            "max_fee": max_fee,
            "gas_premium": gas_premium,
            "start_block": self.wakeup_block,
        }

    def worst_expected_basefee(self, current_basefee):
        basefee_bounds = get_basefee_bounds(current_basefee, self.expected_time(params = {}))
        return basefee_bounds["ub"]

    def transact(self, params):
        basefee = params["basefee"]

        tx_params = self.decide_parameters()

        # expected_gas_price = min(self.worst_expected_basefee(basefee) + tx_params["gas_premium"], tx_params["max_fee"])
        expected_gas_price = min(basefee + tx_params["gas_premium"], tx_params["max_fee"])
        expected_block = self.wakeup_block + self.expected_time(params = {})
        expected_payoff = self.payoff({
            "gas_price": expected_gas_price,
            "current_block": expected_block,
        })

        if expected_payoff < 0 or tx_params["max_fee"] < 0:
            return None

        tx = Tx1559(
            sender = self.pub_key,
            params = tx_params,
        )
        return tx

class UserPool:

    def __init__(self):
        self.users = {}

    def add_users(self, users):
        for user in users:
            self.users[user.pub_key] = user

    def get_user(self, pub_key):
        return self.users[user.pub_key]

    def export(self):
        df = []
        for user in self.users.values():
            df += [user.export()]
        return pd.DataFrame(df)
