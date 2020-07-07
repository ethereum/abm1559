import asyncio
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

import json

async def run(loop):
    nc = NATS()

    await nc.connect("demo.nats.io:4222", loop=loop)

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print("Received a message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))

    # Simple publisher and async subscriber via coroutine.
    sid = await nc.subscribe("foo", cb=message_handler)

    await nc.publish("foo", json.loads('{"nonce":1,"value":1000000000000000000,"gasPremium":1000000000,"feeCap":10000000000}'))

    # Remove interest in subscription.
    await nc.unsubscribe(sid)

    # Terminate connection to NATS.
    await nc.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()
