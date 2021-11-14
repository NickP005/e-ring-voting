import json


async def throw_error(error, websocket):
    try:
        raise error(websocket)
    except error as e:
        print(e)
        return_var = {"exit": "error", "error": e.id()}
        json_exit = json.dumps(return_var)
        await websocket.send(json_exit)


# async def throw_error(error_id, websocket):
#     if error_id == 1:
#         print("Unknown error websocket related occurred")
#         return_var = {"exit": "error", "error": "01"}
#         json_exit = json.dumps(return_var)
#         await websocket.send(json_exit)
#         return
#     elif error_id == 2:
#         print("Message nonce not valid")
#         return_var = {"exit": "error", "error": "02"}
#         json_exit = json.dumps(return_var)
#         await websocket.send(json_exit)
#         return
#     elif error_id == 3:
#         print("Message content format not valid")
#         return_var = {"exit": "error", "error": "03"}
#         json_exit = json.dumps(return_var)
#         await websocket.send(json_exit)
#         returns
