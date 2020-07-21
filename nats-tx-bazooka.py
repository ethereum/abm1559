# https://github.com/nats-io/asyncio-nats-examples/blob/master/publish_json.py

import asyncio
import json
from nats.aio.client import Client as NATS

async def run():
    nc = NATS()

    await nc.connect(servers = ["nats://3.22.223.170:4222"])

    for i in range(100000):
        if i % 1000 == 0: print(i)
        tx = {
            "nonce": i,
            "value": 1000000000000000000,
            "gasPremium": 1000000000,
            "feeCap": 10000000000,
        }
        await nc.publish("txs", json.dumps(tx).encode())

    # Terminate connection to NATS.
    await nc.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
loop.close()
