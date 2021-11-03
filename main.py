# https://websockets.readthedocs.io/en/3.0/intro.html

import asyncio
import binascii

import server_h
import client_h
import connections_h


async def my_super_loop():
    await client_h.checkConnectionWith("192.168.1.151")
    await asyncio.sleep(2)

    # repeats the task forever
    asyncio.create_task(my_super_loop())


async def start_all():
    print("starting voting blockchain node v0.1")
    print("starting websocket server..")
    asyncio.ensure_future(server_h.start_server)
    asyncio.ensure_future(my_super_loop())
    asyncio.ensure_future(connections_h.askForFriends())


asyncio.get_event_loop().run_until_complete(
    start_all()
)
asyncio.get_event_loop().run_forever()
