import json
import random
from .file import json_files
from handlers import client, server, connections
from exceptions import *

nonce_list = []
nonce_dictionary = {}  # key: nonce, value: [ip]


async def handle_incoming_message(msg, websocket):
    print("message received")
    try:
        message_dict = json.loads(msg)
        message_aim = message_dict["aim"]
        message_nonce = message_dict["nonce"]
        await save_new_nonce_entry(message_nonce, websocket)
        if not await is_unique_nonce(message_nonce):
            # await error.throw_error(2, websocket)
            await throw_error(InvalidNonce, websocket)
            return
        if message_aim == "new_block":
            print("new block to check")

        elif message_aim == "message":
            print("going to check for message")
            await aim_message(message_dict["text"], message_nonce, websocket)
        elif message_aim == "discover_nodes":
            await aim_discover_nodes(websocket)
        elif message_aim == "new_node":
            await aim_new_node(message_dict["nodes"], websocket)
        else:
            print("unknown aim")
    except Exception:
        # await error.throw_error(1, websocket)
        await throw_error(UnknownError, websocket)


async def is_unique_nonce(nonce: str):
    """
    Returns True if nonce is unique and valid
    """
    if nonce in nonce_list or len(nonce) != 8 or not nonce.isnumeric():
        return False
    if len(nonce_list) > 99:
        del nonce_list[0]
    nonce_list.append(nonce)
    return True


async def save_new_nonce_entry(nonce, websocket):
    if len(nonce) != 8 or not nonce.isnumeric():
        return False
    if nonce not in nonce_dictionary:
        nonce_dictionary[nonce] = []
    nonce_array = nonce_dictionary[nonce]
    ip, port = websocket.remote_address
    if ip in nonce_array:
        return True
    nonce_array.append(ip)
    nonce_dictionary[nonce] = nonce_array
    return True


async def aim_message(text, nonce, websocket):
    # controlla se il message è una stringa e non abbia caratteri sbagliati es: -/&%$£"!"
    if not isinstance(text, str) or not text.isalnum():
        print("messaggio sbagliato")
        # await error.throw_error(3, websocket)
        await throw_error(InvalidFormat, websocket)
        return False
    # formatti il nuovo messaggio in json e chiami la funzione broadcast_message()
    message_cache = {"aim": "message", "text": text, "nonce": nonce}

    json_message = json.dumps(message_cache)
    await broadcast_message(json_message, nonce)


async def aim_discover_nodes(websocket):
    # Questo websocket ci sta chiedendo che nodi conosce
    # Gli si invia solo i nodi che hanno 5 di attempts
    ip, port = websocket.remote_address
    nodes_to_send = []
    # json_nodes = None

    json_nodes = json_files["data/known_nodes.json"]
    optimal_iterations = 5
    all_nodes = []
    for node_data in json_nodes["nodes"].values():
        if node_data["attempts"] == 5:
            if ip != node_data["ip"]:
                all_nodes.append(node_data["ip"])
    i = 0
    while i < optimal_iterations and i < len(all_nodes):
        random_node = random.choice(all_nodes)
        all_nodes.remove(random_node)
        nodes_to_send.append(random_node)

    random_nonce = ''.join(random.choice("0123456789") for _ in range(8))
    msg_obj = {"aim": "new_node", "nonce": random_nonce, "nodes": nodes_to_send}
    msg = json.dumps(msg_obj)
    print("[]->[", ip, "]", msg)
    await websocket.send(msg)


async def aim_new_node(nodes_array, _websocket):
    if not isinstance(nodes_array, list):
        return False
    impostors = 0  # sus
    for node_ip in nodes_array:
        if impostors == 2:
            return False
        if not await client.connect_to(node_ip):
            impostors += 1
        await connections.save_new_node(node_ip)
    return True


async def broadcast_message(msg, nonce):
    """
    Qui si invia a tutte le persone a cui si è connessi un messaggio, quindi si invia ai client e ai server a cui 
    si è connessi il messaggio, ma prima bisogna controllare che si è connessi ad abbastanza persone (impostate su 
    settings.json)
    """
    await connections.stay_not_alone()

    print("Sto per inviare ", msg)
    nonce_array = nonce_dictionary[nonce]
    for websocket in server.clients_connected:
        ip, port = websocket.remote_address
        if ip in nonce_array:
            print("questo lo conosco gia")
            # continue
        print("sto per inviare un messaggio a ", ip, ":", port)
        await websocket.send(msg)
        nonce_array.append(ip)
    for websocket in client.websocket_connections:
        ip, port = websocket.remote_address
        if ip in nonce_array:
            print("questo lo conosco gia")
            # continue
        await websocket.send(msg)
        nonce_array.append(ip)
    nonce_dictionary[nonce] = nonce_array
    # await asyncio.wait([websocket.send(message) for websocket in server.clients_connected])
    # await asyncio.wait([websocket.send(message) for websocket in client.websocket_connections])
    pass
