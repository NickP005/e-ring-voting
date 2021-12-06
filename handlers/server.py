import asyncio
import websockets
from handlers import message, connections
import socket

clients_connected = set()
local_ip = "0.0.0.0"

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
    #asyncio.get_event_loop()
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

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

async def start():
    global local_ip
    local_ip = get_ip()
    print("Local IP: ", local_ip)
    start_server = websockets.serve(new_connection, local_ip, 25570)
    asyncio.ensure_future(start_server)
