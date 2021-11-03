import websockets
import asyncio
import json, random
from aiofile import async_open

import W_error
import connections_h
import server_h
import client_h

nonce_list = []
nonce_dictionary = {} # key: nonce, value: [ip]

async def handleIncomingMessage(message, websocket):
    print("message received")
    try:
        message_dict = json.loads(message)
        message_aim = message_dict["aim"]
        message_nonce = message_dict["nonce"]
        await saveNewNonceEntry(message_nonce, websocket)
        if(await checkNonceUniqness(message_nonce) == False):
            await W_error.throwError(2, websocket)
            return
        if(message_aim == "new_block"):
            print("new block to check")

        elif(message_aim == "message"):
            print("going to check for message")
            await aim_message(message_dict["text"], message_nonce, websocket)
        elif(message_aim == "discover_nodes"):
            await aim_discoverNodes(websocket)
        elif(message_aim == "new_node"):
            await aim_newNode(message_dict["nodes"], websocket)
        else:
            print("unknown aim")
    except Exception as err:
        await W_error.throwError(1, websocket)

async def checkNonceUniqness(nonce):
    if nonce in nonce_list:
        return False
    if(len(nonce) != 8 or not nonce.isnumeric()):
        return False
    if len(nonce_list) > 99:
        del nonce_list[0]
    nonce_list.append(nonce)
    return True

async def saveNewNonceEntry(nonce, websocket):
    if(len(nonce) != 8 or not nonce.isnumeric()):
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
    #controlla se il message è una stringa e non abbia caratteri sbagliati es: -/&%$£"!"
    if not isinstance(text, str) or not text.isalnum():
        print("messaggio sbagliato")
        await W_error.throwError(3, websocket)
        return False
    #formatti il nuovo messaggio in json e chiami la funzione broadcast_message()
    message_cache = {"aim": "message", "text": text, "nonce": nonce}

    json_message = json.dumps(message_cache)
    await broadcast_message(json_message, nonce )

async def aim_discoverNodes(websocket):
    #Questo websocket ci sta chiedendo che nodi conosce
    # Gli si invia solo i nodi che hanno 5 di attempts
    ip, port = websocket.remote_address
    nodes_to_send = []
    #json_nodes = None
    async with async_open("data/known_nodes.json", 'r') as afp:
        json_nodes = json.loads(await afp.read())
        optimal_iterations = 5
        all_nodes = []
        for node_data in json_nodes["nodes"].values():
            if(node_data["attempts"] == 5):
                if(ip != node_data["ip"]):
                    all_nodes.append(node_data["ip"])
        iter = 0
        while ( iter < optimal_iterations and iter < len(all_nodes)):
            random_node = random.choice(all_nodes)
            all_nodes.remove(random_node)
            nodes_to_send.append(random_node)
    random_nonce = ''.join(random.choice("0123456789") for i in range(8))
    message_obj = {"aim":"new_node", "nonce":random_nonce, "nodes": nodes_to_send}
    message = json.dumps(message_obj)
    print("[]->[",ip,"]",message)
    await websocket.send(message)

async def aim_newNode(nodes_array, websocket):
    if not isinstance(nodes_array, list):
        return False
    impostors = 0
    for node_ip in nodes_array:
        if impostors == 2:
            return False
        if not await client_h.connect_to(node_ip):
            impostors += 1
        await connections_h.saveNewNodeIP(node_ip)
    return True

async def broadcast_message(message, nonce):
    #Qui si invia a tutte le persone a cui si è connessi un messaggio
    #QUindi si invia ai client e ai server a cui si è connessi il messaggio
    #Ma prima bisogna controllare che si è connessi ad abbastanza persone (impostate su settings.json)
    await connections_h.stayNotAlone()

    print("Sto per inviare ", message)
    nonce_array = nonce_dictionary[nonce]
    for websocket in server_h.clients_connected:
        ip, port = websocket.remote_address
        if ip in nonce_array:
            print("questo lo conosco gia")
            #continue
        print("sto per inviare un messaggio a ", ip, ":", port)
        await websocket.send(message)
        nonce_array.append(ip)
    for websocket in client_h.websocket_connections:
        ip, port = websocket.remote_address
        if ip in nonce_array:
            print("questo lo conosco gia")
            #continue
        await websocket.send(message)
        nonce_array.append(ip)
    nonce_dictionary[nonce] = nonce_array
    #await asyncio.wait([websocket.send(message) for websocket in server_h.clients_connected])
    #await asyncio.wait([websocket.send(message) for websocket in client_h.websocket_connections])
    pass
