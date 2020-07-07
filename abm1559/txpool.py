class TxPool:

    def __init__(self):
        self.txs = {}
        self.pool_length = 0

    def add_txs(self, txs):
        for tx in txs:
            self.txs[tx.tx_hash] = tx
        self.pool_length += len(txs)

    def remove_txs(self, tx_hashes):
        for tx_hash in tx_hashes:
            del(self.txs[tx_hash])
        self.pool_length -= len(tx_hashes)

    def average_tip(self, params): # in Gwei
        return 0 if self.pool_length == 0 else sum([tx.tip(params) for tx in self.txs.values()]) / self.pool_length / (10 ** 9)

    def __str__(self):
        return "\n".join([tx.__str__() for tx in self.txs.values()])
