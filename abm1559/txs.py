from abm1559.config import rng

from abm1559.utils import (
    constants,
)

class Transaction:
    """
    An abstract superclass for transactions.
    """

    def __init__(self, sender, tx_params, gas_used=constants["SIMPLE_TRANSACTION_GAS"], tx_hash=None, rng=rng):
        self.sender = sender
        self.start_block = tx_params["start_block"]
        self.gas_used = gas_used

        if tx_hash is None:
            self.tx_hash = rng.bytes(8)
        else:
            self.tx_hash = tx_hash

    def tx_data(self, env):
        return {
            "tx": self,
            "start_block": self.start_block,
            "sender": self.sender.hex(),
            "gas_used": self.gas_used,
            "tx_hash": self.tx_hash.hex(),
        }

class Tx1559(Transaction):
    """
    Inherits from :py:class:`abm1559.txs.Transaction`. A 1559-type transaction.
    """

    def __init__(self, sender, tx_params, **kwargs):
        super().__init__(sender, tx_params, **kwargs)

        self.gas_premium = tx_params["gas_premium"]
        self.max_fee = tx_params["max_fee"]

    def __str__(self):
        return f"1559 Transaction {self.tx_hash.hex()}: max_fee {self.max_fee}, gas_premium {self.gas_premium}"

    def is_valid(self, env):
        basefee = env["basefee"]
        return self.max_fee >= basefee

    def gas_price(self, env):
        # What the user pays
        basefee = env["basefee"]
        return min(self.max_fee, basefee + self.gas_premium)

    def tip(self, env):
        # What the miner gets
        basefee = env["basefee"]
        return self.gas_price(env) - basefee

    def tx_data(self, env):
        return {
            **super().tx_data(env),
            "gas_premium": self.gas_premium / (10 ** 9),
            "max_fee": self.max_fee / (10 ** 9),
            "tip": self.tip(env) / (10 ** 9),
        }

class TxEscalator(Transaction):
    """
    Inherits from :py:class:`abm1559.txs.Transaction`. An escalator-type transaction.
    """

    def __init__(self, sender, tx_params, **kwargs):
        super().__init__(sender, tx_params, **kwargs)

        self.max_block = tx_params["max_block"]
        self.start_premium = tx_params["start_premium"]
        self.max_premium = tx_params["max_premium"]

    def __str__(self):
        return f"Escalator Transaction {self.tx_hash.hex()}: start block {self.start_block}, " + \
                f"max block {self.max_block}, start premium {self.start_premium}, max premium {self.max_premium}"

    def is_valid(self, env):
        current_block = env["current_block"]
        return self.start_block <= current_block and current_block <= self.max_block

    def gas_price(self, env):
        # What the user pays
        current_block = env["current_block"]
        fraction_elapsed = (current_block - self.start_block) / (self.max_block - self.start_block)
        return self.start_premium + fraction_elapsed * (self.max_premium - self.start_premium)

    def tip(self, env):
        # What the miner gets
        # In the escalator, miner gets the whole gas_price
        return self.gas_price(env)

class TxFloatingEsc(Transaction):
    """
    Inherits from :py:class:`abm1559.txs.Transaction`. A floating escalator-type transaction.
    """

    def __init__(self, sender, tx_params, **kwargs):
        super().__init__(sender, tx_params, **kwargs)

        self.max_block = tx_params["max_block"]
        self.start_premium = tx_params["start_premium"]

        if "max_fee" in tx_params and "max_premium" not in tx_params:
            self.max_fee = tx_params["max_fee"]
            self.max_premium = self.max_fee - tx_params["basefee"]
        elif "max_fee" not in tx_params and "max_premium" in tx_params:
            self.max_premium = tx_params["max_premium"]
            self.max_fee = tx_params["basefee"] + self.max_premium
        elif "max_fee" in tx_params and "max_premium" in tx_params:
            self.max_fee = tx_params["max_fee"]
            self.max_premium = tx_params["max_premium"]

    def __str__(self):
        return f"Floating Escalator Transaction {self.tx_hash.hex()}: start block {self.start_block}, " + \
                f"max block {self.max_block}, start premium {self.start_premium}, max premium {self.max_premium}, " + \
                f"max fee {self.max_fee}"

    def is_valid(self, env):
        current_block = env["current_block"]
        basefee = env["basefee"]
        return self.start_block <= current_block and current_block <= self.max_block and basefee <= self.max_fee

    def gas_price(self, env):
        # What the user pays
        current_block = env["current_block"]
        basefee = env["basefee"]

        if self.start_block == self.max_block:
            return min(self.max_fee, basefee + self.start_premium)

        fraction_elapsed = (current_block - self.start_block) / (self.max_block - self.start_block)
        gas_premium = self.start_premium + fraction_elapsed * (self.max_premium - self.start_premium)
        return min(self.max_fee, basefee + gas_premium)

    def tip(self, env):
        # What the miner gets
        basefee = env["basefee"]
        return self.gas_price(env) - basefee

    def tx_data(self, env):
        return {
            **super().tx_data(env),
            "start_premium": self.start_premium / (10 ** 9),
            "max_fee": self.max_fee / (10 ** 9),
            "tip": self.tip(env) / (10 ** 9),
        }

class TxLegacy(Transaction):
    """
    Inherits from :py:class:`abm1559.txs.Transaction`. A legacy-type transaction.
    """
    def __init__(self, sender, tx_params, **kwargs):
        super().__init__(sender, tx_params, **kwargs)

        self._gas_price = tx_params["gas_price"]
        
    def gas_price(self, env={}):
        # What the user pays
        return self._gas_price
    
    def tip(self, env={}):
        # What the miner gets
        return self.gas_price(env)

    def __str__(self):
        return f"Legacy Transaction {self.tx_hash.hex()}: gas_price {self.gas_price}"

    def tx_data(self, env):
        return {
            **super().tx_data(env),
            "gas_price": self.gas_price / (10 ** 9),
        }
