from typing import Sequence, Dict

import pandas as pd

from abm1559.txs import Transaction
from abm1559.users import User

class UserPool:

    def __init__(self):
        self.users = {}

    def decide_transactions(self, users: Sequence[User], env: Dict) -> Sequence[Transaction]:
        """
        Adds and queries all new users, to check who wants to send transactions and who wants to balk.

        Args:
            users (Sequence[User]): Sequence of new users
            env (Dict): Current simulation environment parameters (e.g., basefee)

        Returns:
            Sequence[Transaction]: An array of transactions
        """

        txs = []
        for user in users:
            self.users[user.pub_key] = user
            tx = user.transact(env)
            if not tx is None:
                txs.append(tx)

        return txs

    def get_user(self, pub_key):
        return self.users[pub_key]

    def cancel_transactions(self, txpool, env):
        """
        Queries all users and checks who wants to cancel their transactions waiting in the pool.

        Args:
            txpool (TxPool): Transaction pool

        Returns:
            Sequence[bytes]: An array of transaction hashes
        """

        cancelled_txs = []
        for tx in txpool.txs.values():
            user = get_user(tx.sender)
            cancel = user.cancel(tx, env)
            if cancel:
                cancelled_txs += [tx.tx_hash]
        return cancelled_txs

    def export(self):
        df = []
        for user in self.users.values():
            df += [user.export()]
        return pd.DataFrame(df)
