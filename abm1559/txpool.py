from typing import Sequence

from abm1559.txs import Transaction

from abm1559.utils import (
    rng,
    constants,
)

class TxPool:
    """
    Represents the transaction queue.
    """

    def __init__(self):
        self.txs = {}
        self.pool_length = 0

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
        self.pool_length += len(txs)

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
        self.pool_length -= len(tx_hashes)

    def cancel_txs(self, tx_hashes: Sequence[str], cancel_cost):
        """
        Cancels a transaction from the queue, indexed by `tx_hashes`.
        Assumes a fixed cancel cost
        """
        for tx_hash in tx_hashes:
            tx = self.txs[tx_hash]
            tx.gas_used = 0
            tx.tip = tx.tip + cancel_cost
            self.txs[tx_hash] = tx

    def average_tip(self, params): # in Gwei
        if self.pool_length == 0:
            return 0
        else:
            return sum([tx.tip(params) for tx in self.txs.values()]) / self.pool_length / (10 ** 9)

    def average_gas_price(self, params):
        if self.pool_length == 0:
            return 0
        else:
            return sum([tx.gas_price(params) for tx in self.txs.values()]) / self.pool_length / (10 ** 9)

    def select_transactions(self, params):
        # Miner side
        basefee = params["basefee"]
        max_tx_in_block = int(constants["MAX_GAS_EIP1559"] / constants["SIMPLE_TRANSACTION_GAS"])

        valid_txs = [tx for tx in self.txs.values() if tx.is_valid({ "basefee": basefee })]
        rng.shuffle(valid_txs)

        sorted_valid_demand = sorted(
            valid_txs,
            key = lambda tx: -tx.tip({ "basefee": basefee })
        )
        selected_txs = sorted_valid_demand[0:max_tx_in_block]

        return selected_txs

    def average_value(self, user_pool):
        avg = 0.0
        for tx in self.txs.values():
            sender = user_pool.users[tx.sender]
            avg += sender.value / self.pool_length
        return avg

    def average_waiting_time(self, current_height):
        return 0 if len(self.txs) == 0 else sum([current_height - tx.start_block for tx in self.txs.values()]) / len(self.txs)

    def __str__(self):
        return "\n".join([tx.__str__() for tx in self.txs.values()])
