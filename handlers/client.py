import asyncio
import websockets


from handlers import message, server, connections

websocket_connections = set()


async def connect_to(ip):
    websocket = None
    if await check_connection_with(ip):
        print("already connected with this node")
        return True  # true?
    try:
        websocket = await asyncio.wait_for(websockets.connect("ws://" + ip + ":25570"), timeout=5)
        asyncio.create_task(receive_message_callback(await asyncio.wait_for(websocket.recv(), timeout=500), websocket))
        websocket_connections.add(websocket)
        await connections.save_new_node(ip)
    except websockets.InvalidURI:
        print("Invalid node URL: ", "ws://" + ip + ":25570")
        return False
    except ConnectionTimeoutError:  # non esiste questa Exception, prova a rivedere
        print("Timeout error with " + ip + ":25570")
        return False
    except websockets.ConnectionClosedOK:
        print("Closed connection with " + ip + ":25570")
        return False
    except Exception as e:
        print("Unhandled error.")
        print(e)
    finally:
        # print(websocket)
        return websocket is not None


async def receive_message_callback(msg, websocket):
    ip, port = websocket.remote_address
    stripped = msg.replace('\n', '').replace('\t', '')
    print(f"New message from serve {ip}: {stripped[:22]} {'[...]' if len(stripped) > 22 else ''}")
    await message.handle_incoming_message(msg, websocket)
    asyncio.create_task(receive_message_callback(await asyncio.wait_for(websocket.recv(), timeout=500), websocket))


async def check_connection_with(ip_check):
    # First check if that IP is already connected to US
    # print("connesso da: ")
    for websocket in server.clients_connected:
        ip, port = websocket.remote_address
        # print("{} : {}".format(ip, port))
        if ip_check == ip:
            return True
    return False
