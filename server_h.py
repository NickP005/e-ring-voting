import asyncio
import websockets
import messageHandler

import connections_h
clients_connected = set()



async def register(websocket):
    ip, port = websocket.remote_address
    print("New client connected {}".format(ip))
    clients_connected.add(websocket)
    await connections_h.saveNewNodeIP(ip)

async def unregister(websocket):
    ip, port = websocket.remote_address
    print("Client {} disconnected".format(ip))
    clients_connected.remove(websocket)

async def new_connection(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    loop = asyncio.get_event_loop()
    try:
        async for message in websocket:
            #geniale
            stripped = message.replace('\n', '').replace('\t', '')
            if len(message) > 22:
                stipped = stripped[:22]

            await messageHandler.handleIncomingMessage(message, websocket)
    except ConnectionResetError as error:
        print("Connection Reset Error;")
        print(error)
        return
    except websockets.exceptions.ConnectionClosedError as error:
        pass
    finally:
        print("Client disconnnected")
        await unregister(websocket)
        #await notify_users()

start_server = websockets.serve(new_connection, '192.168.1.233', 25570)
