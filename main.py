# https://websockets.readthedocs.io/en/3.0/intro.html

import asyncio
from handlers import file, connections, server  # , client
from mining import *  # import classes "Mining" and "Block" as set in mining/__init__.py
# from exceptions import *


async def my_super_loop():
    # await client.check_connection_with("192.168.1.151")
    await asyncio.sleep(10)
    await connections.ask_for_friends()

    # repeats the task forever
    asyncio.create_task(my_super_loop())


async def start_all():
    print("starting voting blockchain node v0.1")
    print("starting websocket server..")
    await file.load_dict()
    await server.start()
    asyncio.ensure_future(my_super_loop())  # better to use create_task instead of ensure_future :/
    asyncio.ensure_future(file.write_json())
    # asyncio.ensure_future(connections.ask_for_friends())
    asyncio.ensure_future(Mining().init())
    asyncio.ensure_future(Block().init())


def main():
    asyncio.get_event_loop().run_until_complete(start_all())
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
