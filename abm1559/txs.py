from abm1559.utils import (
    rng,
    constants,
)

class Transaction:
    """
    An abstract superclass for transactions.
    """

    def __init__(self, sender, params, gas_used = constants["SIMPLE_TRANSACTION_GAS"]):
        self.sender = sender
        self.start_block = params["start_block"]
        self.gas_used = gas_used
        self.tx_hash = rng.bytes(8)

    def tx_data(self):
        return {
            "tx": self,
            "start_block": self.start_block,
            "sender": self.sender,
            "gas_used": self.gas_used,
            "tx_hash": self.tx_hash,
        }

class Tx1559(Transaction):
    """
    Inherits from :py:class:`abm1559.txs.Transaction`. A 1559-type transaction.
    """

    def __init__(self, sender, params, gas_used = constants["SIMPLE_TRANSACTION_GAS"]):
        super().__init__(sender, params, gas_used = gas_used)

        self.gas_premium = params["gas_premium"]
        self.max_fee = params["max_fee"]

    def __str__(self):
        return f"1559 Transaction {self.tx_hash.hex()}: max_fee {self.max_fee}, gas_premium {self.gas_premium}"

    def is_valid(self, params):
        basefee = params["basefee"]
        return self.max_fee >= basefee

    def gas_price(self, params):
        # What the user pays
        basefee = params["basefee"]
        return min(self.max_fee, basefee + self.gas_premium)

    def tip(self, params):
        # What the miner gets
        basefee = params["basefee"]
        return self.gas_price(params) - basefee

    def tx_data(self, params):
        return {
            **super().tx_data(),
            "gas_premium": self.gas_premium / (10 ** 9),
            "max_fee": self.max_fee / (10 ** 9),
            "tip": self.tip(params),
        }

class TxEscalator(Transaction):
    """
    Inherits from :py:class:`abm1559.txs.Transaction`. An escalator-type transaction.
    """

    def __init__(self, sender, params, gas_used = constants["SIMPLE_TRANSACTION_GAS"]):
        super().__init__(sender, params, gas_used = gas_used)

        self.max_block = params["max_block"]
        self.start_premium = params["start_premium"]
        self.max_premium = params["max_premium"]

    def __str__(self):
        return f"Escalator Transaction {self.tx_hash.hex()}: start block {self.start_block}, " + \
                f"max block {self.max_block}, start premium {self.start_premium}, max premium {self.max_premium}"

    def is_valid(self, params):
        current_block = params["current_block"]
        return self.start_block <= current_block and current_block <= self.max_block

    def gas_price(self, params):
        # What the user pays
        current_block = params["current_block"]
        fraction_elapsed = (current_block - self.start_block) / (self.max_block - self.start_block)
        return self.start_premium + fraction_elapsed * (self.max_premium - self.start_premium)

    def tip(self, params):
        # What the miner gets
        # In the escalator, miner gets the whole gas_price
        return self.gas_price(params)
