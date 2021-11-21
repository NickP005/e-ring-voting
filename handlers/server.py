import asyncio
import websockets
from handlers import message, connections

clients_connected = set()


async def register(websocket):
    ip, port = websocket.remote_address
    print(f"New client connected {ip}")
    clients_connected.add(websocket)
    await connections.save_new_node(ip)


async def unregister(websocket):
    ip, port = websocket.remote_address
    print(f"Client {ip} disconnected")
    clients_connected.remove(websocket)


async def new_connection(websocket, _path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    asyncio.get_event_loop()
    try:
        async for msg in websocket:
            await message.handle_incoming_message(msg, websocket)
    except ConnectionResetError as error:
        print("Connection Reset Error;")
        print(error)
        return
    except websockets.ConnectionClosedError:
        pass
    finally:
        print("Client disconnected")
        await unregister(websocket)
        # await notify_users()


start_server = websockets.serve(new_connection, '0.0.0.0', 25570)
