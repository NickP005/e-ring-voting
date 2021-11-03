import asyncio
import websockets

import server_h
import messageHandler
import connections_h

websocket_connections = set()


async def connect_to(ip):
    websocket = None
    if await checkConnectionWith(ip):
        print("already connected with this node")
        return True  # true?
    try:
        websocket = await asyncio.wait_for(websockets.connect("ws://" + ip + ":25570"), timeout=5)
        asyncio.create_task(receive_message_callback(await asyncio.wait_for(websocket.recv(), timeout=500), websocket))
        websocket_connections.add(websocket)
        await connections_h.saveNewNodeIP(ip)
    except websockets.exceptions.InvalidURI as error:
        print("Invalid node URL: ", "ws://" + ip + ":25570")
        return False
    except ConnectionTimeoutError as error:
        print("Timeout error with " + ip + ":25570")
        return False
    except websockets.exceptions.ConnectionClosedOK as error:
        print("Closed connection with " + ip + ":25570")
        return False
    except Exception as e:
        print("Unhandled error.")
        print(e)
    finally:
        # print(websocket)
        if (websocket == None):
            return False
        return True


async def receive_message_callback(message, websocket):
    ip, port = websocket.remote_address
    stripped = message.replace('\n', '')
    stripped = stripped.replace('\t', '')
    if (len(message) > 22):
        print("New message from server " + ip + ": " + stripped[:22] + " [...]")
    else:
        print("New message from server " + ip + ": " + stripped)
    await messageHandler.handleIncomingMessage(message, websocket)
    asyncio.create_task(receive_message_callback(await asyncio.wait_for(websocket.recv(), timeout=500), websocket))


async def checkConnectionWith(ip_check):
    # First check if that IP is already connected to US
    # print("connesso da: ")
    for websocket in server_h.clients_connected:
        ip, port = websocket.remote_address
        # print("{} : {}".format(ip, port))
        if ip_check == ip:
            return True

    # print("connesso con: ")
    for websocket in websocket_connections:
        ip, port = websocket.remote_address
        if ip_check == ip:
            return True
        # print("{} : {}".format(ip, port))
    return False
