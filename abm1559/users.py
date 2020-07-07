from abm1559.utils import (
    get_basefee_bounds,
    rng
)

from abm1559.txs import Tx1559

class User:

    def __init__(self, wakeup_block):
        self.pub_key = rng.bytes(8)
        self.wakeup_block = wakeup_block

        # Users have a value / Gwei for the transaction
        self.value = int(rng.uniform(low = 0, high = 20) * (10 ** 9))

    def payoff(self, params):
        gas_price = params["gas_price"]
        return self.cost(params) - gas_price

class AffineUser(User):

    def __init__(self, wakeup_block):
        super().__init__(wakeup_block)
        self.cost_per_unit = int(rng.uniform(low = 0, high = 1) * (10 ** 9))

    def __str__(self):
        return f"Affine User with value {self.value} and cost {self.cost_per_unit}"

    def cost(self, params):
        current_block = params["current_block"]
        elapsed_time = current_block - self.wakeup_block
        return self.value - self.cost_per_unit * elapsed_time

class DiscountUser(User):

    def __init__(self, wakeup_block):
        super().__init__(wakeup_block)
        self.discount_rate = 0.01

    def __str__(self):
        return f"Discount User with value {self.value} and discount rate {self.discount_rate}"

    def cost(self, params):
        current_block = params["current_block"]
        elapsed_time = current_block - self.wakeup_block
        return self.value * (1 - self.discount_rate) ** elapsed_time

class User1559(AffineUser):
    # Expects to be included within 5 blocks
    # Prefers not to participate if its expected payoff is negative
    # Computes expected payoff by estimating the worst possible basefee 5 blocks from now
    # Fixed gas_premium

    def expected_time(self, params):
        return 5

    def decide_parameters(self):
        return {
            "max_fee": self.value - self.expected_time(params = {}) * self.cost_per_unit,
            "gas_premium": 1 * (10 ** 9),
            "start_block": self.wakeup_block,
        }

    def worst_expected_basefee(self, current_basefee):
        basefee_bounds = get_basefee_bounds(current_basefee, self.expected_time(params = {}))
        return basefee_bounds["ub"]

    def transact(self, params):
        basefee = params["basefee"]

        tx_params = self.decide_parameters()

        expected_gas_price = min(self.worst_expected_basefee(basefee) + tx_params["gas_premium"], tx_params["max_fee"])
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
