import sys
import pandas as pd

from abm1559.utils import rng

class Block:
    """
    An abstract block representation.
    """

    def __init__(self, txs, parent_hash, height):
        self.block_hash = rng.bytes(8)
        self.txs = txs
        self.parent_hash = parent_hash
        self.height = height

    def __str__(self):
        return "Block:\n" + "\n".join([tx.__str__() for tx in self.txs])

    def average_waiting_time(self):
        return 0 if len(self.txs) == 0 else sum([self.height - tx.start_block for tx in self.txs]) / len(self.txs)

class Block1559(Block):
    """
    Blocks filled up with 1559 transactions (see :py:class:`abm1559.chain.Tx1559`).
    """

    def __init__(self, txs, parent_hash, height, basefee):
        super().__init__(txs, parent_hash, height)
        self.basefee = basefee

    def average_tip(self): # in Gwei
        return 0 if len(self.txs) == 0 else sum([tx.tip({
            "basefee": self.basefee,
            "current_block": self.height,
        }) for tx in self.txs]) / len(self.txs) / (10 ** 9)

    def average_gas_price(self): # in Gwei
        return 0 if len(self.txs) == 0 else sum([tx.gas_price({
            "basefee": self.basefee,
            "current_block": self.height,
        }) for tx in self.txs]) / len(self.txs) / (10 ** 9)

    def min_premium(self): # in wei
        return 0 if len(self.txs) == 0 else min([tx.gas_premium for tx in self.txs])

    def txs_data(self):
        txs_data = []
        for tx_index, tx in enumerate(self.txs):
            txs_data += [{
                "block_height": self.height,
                "tx_index": tx_index,
                "basefee": self.basefee / (10 ** 9), # in Gwei
                **tx.tx_data({
                    "basefee": self.basefee
                }),
            }]
        return txs_data

class Chain:
    """
    A container for :py:class:`abm1559.chain.Block` .
    """

    def __init__(self):
        self.blocks = {}
        self.current_head = (0).to_bytes(8, sys.byteorder)

    def add_block(self, block):
        self.blocks[block.block_hash] = block
        self.current_head = block.block_hash

    def export(self):
        df = []
        for block in self.blocks.values():
            df += block.txs_data()
        return pd.DataFrame(df)
