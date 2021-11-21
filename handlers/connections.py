import json
import random
from .file import json_files
from handlers import message, client, server

known_nodes_obj = None

ask_for_friends_ips = set()


# Da rivedere
async def load_known_nodes():
    """
    Questa funzione non è usata da nessuna parte e secondo me è molto inutile
    """
    return_var = False
    data = None
    try:
        data = json_files["net_nodes.json"]
    finally:
        with open('net_nodes.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)
            # print("saved JSON file")
            json_file.close()
            return return_var

"""
async def stayNotAlone(min_connections=2):
    # questo dopo sarà preso da un json
    current_connections = len(server.clients_connected) + len(client.websocket_connections)
    print("Connesso con", current_connections, "nodi")
    if current_connections >= min_connections:
        return True
    json_nodes = None
    # Ora si controlla su net_nodes.json se ci sono nodi a cui ci si può connettere in piu
    async with async_open("known_nodes.json", 'r') as afp:
        json_nodes = json.loads(await afp.read())
        print(json_nodes)
        print(json_nodes["nodes"])
        for node_data in json_nodes["nodes"].values():
            if node_data["attempts"] == 0:
                continue
            print("controllo se sono gia connesso con quel nodo")
            if await client.checkConnectionWith(node_data["ip"]):
                print("sono gia connesso con", node_data["ip"])
                continue
            print("mi connetterò a", node_data["ip"])
            if await client.connect_to(node_data["ip"]):
                current_connections += 1
                node_data["attempts"] = 5
                if current_connections >= min_connections:
                    return True
                continue
            # adesso teoricamente dovremmo ridurre attempts di questo nodo di -1
            print("fallito a connettersi a", node_data["ip"])
            node_data["attempts"] -= 1
    async with async_open("known_nodes.json", 'w+') as afp:
        result = json.dumps(json_nodes, indent=4)
        await afp.write(result)
"""


async def stay_not_alone(min_connections=2):
    # questo dopo sarà preso da un json
    current_connections = len(server.clients_connected) + len(client.websocket_connections)
    print("Connesso con", current_connections, "nodi")
    if current_connections >= min_connections:
        return True
    # Ora si controlla su net_nodes.json se ci sono nodi a cui ci si può connettere in piu
    json_nodes = json_files["known_nodes.json"]
    print("nodes", json_nodes["nodes"])
    for node_data in list(json_nodes["nodes"].values()):
        if node_data["attempts"] == 0:
            continue
        print("controllo se sono gia connesso con quel nodo")
        if await client.check_connection_with(node_data["ip"]):
            print("sono gia connesso con", node_data["ip"])
            continue
        print("mi connetterò a", node_data["ip"])
        if await client.connect_to(node_data["ip"]):
            current_connections += 1
            node_data["attempts"] = 5
            if current_connections >= min_connections:
                return True
            continue
        # adesso teoricamente dovremmo ridurre attempts di questo nodo di -1
        print("fallito a connettersi a", node_data["ip"])
        node_data["attempts"] -= 1


"""
async def saveNewNodeIP(ip):
    async with async_open("known_nodes.json", 'r') as afp:
        json_nodes = json.loads(await afp.read())
    async with async_open("known_nodes.json", 'w+') as afp:
        if ip in json_nodes["nodes"].values():
            return True
        json_nodes["nodes"][ip] = {"ip": ip, "attempts": 5}
        result = json.dumps(json_nodes, indent=4)
        await afp.write(result)
"""


async def save_new_node(ip):
    """
    Saves new node's ip in known nodes json file
    :param ip: ip of the node to be saved
    """
    if ip == "127.0.0.1":
        print("Won't save 127.0.0.1")
        return False
    json_nodes = json_files["known_nodes.json"]
    if ip in json_nodes["nodes"].values():
        return True
    json_nodes["nodes"][ip] = {"ip": ip, "attempts": 5}


# Asks to all of the connected nodes their node list IPs
"""
async def askForFriends():
    #Connects at least with 2 nodes
    await stayNotAlone()
    random_nonce = ''.join(random.choice("0123456789") for i in range(8)) # Te l'ho riscritto chiamo la reda
    message_obj = {"aim":"discover_nodes", "nonce":random_nonce}
    message = json.dumps(message_obj)
    print("mando ", message)
    for websocket in server.clients_connected:
        ip, port = websocket.remote_address
        await websocket.send(message)
        ask_for_friends_ips.add(ip)
    for websocket in client.websocket_connections:
        ip, port = websocket.remote_address
        await websocket.send(message)
        ask_for_friends_ips.add(ip)
        """


async def ask_for_friends():
    random_nonce = ''.join(random.choice("0123456789") for _ in range(8))  # Te l'ho riscritto chiamo la reda
    msg_obj = {"aim": "discover_nodes", "nonce": random_nonce}
    msg = json.dumps(msg_obj)
    await message.broadcast_message(msg, random_nonce)
