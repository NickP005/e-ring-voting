# https://websockets.readthedocs.io/en/3.0/intro.html

import asyncio
from handlers import client, connections, server, file


async def my_super_loop():
    await client.check_connection_with("192.168.1.151")
    await asyncio.sleep(2)

    # repeats the task forever
    asyncio.create_task(my_super_loop())


async def start_all():
    print("starting voting blockchain node v0.1")
    print("starting websocket server..")
    asyncio.ensure_future(file.load_dict())
    asyncio.ensure_future(server.start_server)
    asyncio.ensure_future(my_super_loop())
    asyncio.ensure_future(file.write_json())
    asyncio.ensure_future(connections.ask_for_friends())

asyncio.get_event_loop().run_until_complete(
    start_all()
)
asyncio.get_event_loop().run_forever()
