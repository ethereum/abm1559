from typing import Sequence

from abm1559.config import rng

from abm1559.txs import Transaction

from abm1559.utils import (
    constants,
)

class TxPool:
    """
    Represents the transaction queue.
    """

    def __init__(self):
        self.txs = {}
        
    def pool_length(self) -> int:
        return len(self.txs)

    def add_txs(self, txs: Sequence[Transaction]) -> None:
        """
        Adds `txs` to the queue.

        Args:
            txs (Sequence[Transaction]): The transactions to add

        Returns:
            None
        """

        for tx in txs:
            self.txs[tx.tx_hash] = tx

    def remove_txs(self, tx_hashes: Sequence[str]):
        """
        Removes transactions from the queue, indexed by `tx_hashes`.

        Args:
            txs (Sequence[Transaction]): The transactions to add

        Returns:
            None
        """

        for tx_hash in tx_hashes:
            del(self.txs[tx_hash])
        
    def empty_pool(self):
        """
        Removes all transactions from the queue.
        
        Returns:
            None
        """
        self.txs = {}

    def cancel_txs(self, tx_hashes: Sequence[str], cancel_cost):
        """
        Cancels a transaction from the queue, indexed by `tx_hashes`.
        Assumes a fixed cancel cost
        """
        for tx_hash in tx_hashes:
            tx = self.txs[tx_hash]
            tx.gas_used = 0
            tx.gas_premium = tx.gas_premium + cancel_cost
            self.txs[tx_hash] = tx

    def average_tip(self, env): # in Gwei
        if self.pool_length == 0:
            return 0
        else:
            return sum([tx.tip(env) for tx in self.txs.values()]) / self.pool_length() / (10 ** 9)

    def average_gas_price(self, env):
        if self.pool_length == 0:
            return 0
        else:
            return sum([tx.gas_price(env) for tx in self.txs.values()]) / self.pool_length() / (10 ** 9)

    def select_transactions(self, env, user_pool=None, rng=rng):
        # Miner side
        max_tx_in_block = int(constants["MAX_GAS_EIP1559"] / constants["SIMPLE_TRANSACTION_GAS"])

        valid_txs = [tx for tx in self.txs.values() if tx.is_valid(env)]
        rng.shuffle(valid_txs)

        sorted_valid_demand = sorted(
            valid_txs,
            key = lambda tx: -tx.tip(env)
        )
        selected_txs = sorted_valid_demand[0:max_tx_in_block]

        return selected_txs

    def average_value(self, user_pool):
        avg = 0.0
        for tx in self.txs.values():
            sender = user_pool.get_user(tx.sender)
            avg += sender.value / self.pool_length()
        return avg

    def average_waiting_time(self, current_height):
        return 0 if len(self.txs) == 0 else sum([current_height - tx.start_block for tx in self.txs.values()]) / len(self.txs)

    def __str__(self):
        return "\n".join([tx.__str__() for tx in self.txs.values()])
