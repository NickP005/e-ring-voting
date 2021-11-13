import json


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
#         return


async def throw_error(error, websocket):
    try:
        raise error(websocket)
    except error as e:
        print(e)


class Error(Exception):
    def __init__(self, error_id, websocket, message):
        self.message = message
        self.error_id = error_id
        self.websocket = websocket

        return_var = {"exit": "error", "error": str(error_id).zfill(2)}
        json_exit = json.dumps(return_var)

        # await websocket.send(json_exit)
        websocket.send(json_exit)

        super(Error, self).__init__(self.message)

    def __str__(self):
        return self.message

    def __repr__(self):
        return f"error id {self.error_id}: {self.message}"


class UnknownError(Error):
    def __init__(self, websocket):
        message = "An unknown websocket related error has occurred"
        super().__init__(1, websocket, message)


class InvalidNonce(Error):
    def __init__(self, websocket):
        message = "The message nonce is not valid"
        super().__init__(2, websocket, message)


class InvalidFormat(Error):
    def __init__(self, websocket):
        message = "The message content format is not valid"
        super().__init__(3, websocket, message)