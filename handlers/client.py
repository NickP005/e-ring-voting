import asyncio
import websockets

from handlers import message, server, connections

websocket_connections = set()


async def connect_to(ip):
    websocket = None
    if await check_connection_with(ip):
        #print(f"already connected with {ip} node")
        return True  # true?
    try:
        websocket = await asyncio.wait_for(websockets.connect("ws://" + ip + ":25570"), timeout=1)
        asyncio.create_task(receive_message_callback("", websocket ) )
        websocket_connections.add(websocket)
        await connections.save_new_node(ip)
        #print("obtained websocket")
        return websocket

    except websockets.InvalidURI:
        print("Invalid node URL: ", "ws://" + ip + ":25570")
        return False
    except websockets.ConnectionTimeoutError:  # non esiste questa Exception, prova a rivedere
        print("Timeout error with " + ip + ":25570")
        return False
    except websockets.ConnectionClosedOK:
        print("Closed connection with " + ip + ":25570")
        return False
    except websockets.ConnectionClosedError:
        print("ConnectionClosedError")
        return False
    except Exception as e:
        print("Unhandled error.")
        print(e)
    finally:
        #print("finally")
        # print(websocket)
        #if websocket is not None:
            #print("creo task")
            #websocket_connections.add(websocket)
            #await connections.save_new_node(ip)
            #asyncio.create_task(receive_message_callback("", websocket ) )
            #asyncio.create_task(receive_message_callback(await asyncio.wait_for(websocket.recv(), timeout=500), websocket))
            #print("saved the ip")
        return websocket is not None


async def receive_message_callback(msg, websocket):
    try:
        #print("receive message callback")
        if(msg == ""):
            asyncio.create_task(receive_message_callback(await asyncio.wait_for(websocket.recv(), timeout=500), websocket))
            return False
        ip, port = websocket.remote_address
        stripped = msg.replace('\n', '').replace('\t', '')
        #print(f"New message from serve {ip}: {stripped[:22]} {'[...]' if len(stripped) > 22 else ''}")
        await message.handle_incoming_message(msg, websocket)
        asyncio.create_task(receive_message_callback(await asyncio.wait_for(websocket.recv(), timeout=500), websocket))
    except websockets.ConnectionClosedError:
        print("ConnectionClosedError receive message callback")
        websocket_connections.remove(websocket)
        return False
    except websockets.IncompleteReadError:
        print("IncompleteReadError")
        return False
    finally:
        pass


async def check_connection_with(ip_check):
    # First check if that IP is already connected to US
    # print("connesso da: ")
    for websocket in server.clients_connected | websocket_connections:
        ip, port = websocket.remote_address
        # print("{} : {}".format(ip, port))
        if ip_check == ip:
            return True
    if ip_check == server.local_ip:
        return True
    return False
