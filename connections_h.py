import os, json, random
import asyncio
from aiofile import async_open

import server_h
import client_h
import messageHandler

known_nodes_obj = None

ask_for_friends_ips = set()

# Da rivedere
async def loadKnownNodes():
    return_var = False
    data = None
    try:
        with open('data/net_nodes.json', 'r') as json_file:
            data = json.load(json_file)

            json_file.close()
    finally:
        with open('data/net_nodes.json', 'w') as json_file:
            result = json.dump(data, json_file, indent=4)
            #print("saved JSON file")
            json_file.close()
            return return_var

async def stayNotAlone(min_connections = 2):
     #questo dopo sarà preso da un json
    current_connections = len(server_h.clients_connected) + len(client_h.websocket_connections)
    print("Connesso con", current_connections, "nodi")
    if(current_connections >= min_connections):
        return True
    json_nodes = None
    #Ora si controlla su data/net_nodes.json se ci sonon nodi a cui ci si può connettere in piu
    async with async_open("data/known_nodes.json", 'r') as afp:
        json_nodes = json.loads(await afp.read())
        print(json_nodes)
        print(json_nodes["nodes"])
        for node_data in json_nodes["nodes"].values():
            if(node_data["attempts"] == 0):
                continue
            print("controllo se sono gia connesso con quel nodo")
            if(await client_h.checkConnectionWith(node_data["ip"])):
                print("sono gia connnesso con", node_data["ip"])
                continue
            print("mi connetterò a", node_data["ip"])
            if(await client_h.connect_to(node_data["ip"])):
                current_connections += 1
                node_data["attempts"] = 5
                if(current_connections >= min_connections):
                    return True
                continue
            #adesso teoricamente dovremmo ridurre attempts di questo nodo di -1
            print("fallito a connettersi a", node_data["ip"])
            node_data["attempts"] -= 1
    async with async_open("data/known_nodes.json", 'w+') as afpp:
        result = json.dumps(json_nodes, indent=4)
        await afpp.write(result)

async def saveNewNodeIP(ip):
    json_nodes = None
    async with async_open("data/known_nodes.json", 'r') as afp:
        json_nodes = json.loads(await afp.read())
    async with async_open("data/known_nodes.json", 'w+') as afp:
        if ip in json_nodes["nodes"].values():
            return True
        json_nodes["nodes"][ip] = {"ip":ip, "attempts":5}
        result = json.dumps(json_nodes, indent=4)
        await afp.write(result)

#Asks to all of the connected nodes their node list IPs
"""
async def askForFriends():
    #Connects at least with 2 nodes
    await stayNotAlone()
    random_nonce = ''.join(random.choice("0123456789") for i in range(8)) # Te l'ho riscritto chiamo la reda
    message_obj = {"aim":"discover_nodes", "nonce":random_nonce}
    message = json.dumps(message_obj)
    print("mando ", message)
    for websocket in server_h.clients_connected:
        ip, port = websocket.remote_address
        await websocket.send(message)
        ask_for_friends_ips.add(ip)
    for websocket in client_h.websocket_connections:
        ip, port = websocket.remote_address
        await websocket.send(message)
        ask_for_friends_ips.add(ip)
        """
async def askForFriends():
    random_nonce = ''.join(random.choice("0123456789") for i in range(8)) # Te l'ho riscritto chiamo la reda
    message_obj = {"aim":"discover_nodes", "nonce":random_nonce}
    message = json.dumps(message_obj)
