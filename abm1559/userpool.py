from typing import Sequence, Dict

import pandas as pd

from abm1559.txs import Transaction
from abm1559.users import User

class UserPool:

    def __init__(self):
        self.users = {}
        
    def add_users(self, users: Sequence[User]) -> None:
        for user in users:
            self.users[user.pub_key] = user
    
    def query_users(self, env: Dict, query_all: bool = False) -> Sequence[Transaction]:
        if query_all:
            users_to_query = self.users.values()
        else:
            users_to_query = [user for user in self.users.values() if user.wakeup_block == env["current_block"]]
        
        txs = []  
        for user in users_to_query:
            tx = user.transact(env)
            if not tx is None:
                txs.append(tx)
        return txs
            

    def decide_transactions(self, users: Sequence[User], env: Dict, query_all: bool = False) -> Sequence[Transaction]:
        """
        Adds and queries all new users, to check who wants to send transactions and who wants to balk.

        Args:
            users (Sequence[User]): Sequence of new users
            env (Dict): Current simulation environment parameters (e.g., basefee)
            query_all (bool): Should all users in the pool be queried, or new incoming users only?

        Returns:
            Sequence[Transaction]: An array of transactions
        """

        txs = []
        if not query_all:
            for user in users:
                self.users[user.pub_key] = user
                tx = user.transact(env)
                if not tx is None:
                    txs.append(tx)
        else:
            for user in users:
                self.users[user.pub_key] = user
            for pub_key, user in self.users.items():
                tx = user.transact(env)
                if not tx is None:
                    txs.append(tx)

        return txs

    def get_user(self, pub_key):
        return self.users[pub_key]

    def export(self):
        df = []
        for user in self.users.values():
            df += [user.export()]
        return pd.DataFrame(df)
