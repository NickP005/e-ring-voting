import asyncio
import json
from aiofile import async_open
import os.path


json_files = {
    "data/net_nodes.json": {},
    "data/known_nodes.json": {}
}


async def load_dict():
    """
    Called when start_all. Loads json_files values.
    """
    for file_name in json_files.keys():

        assert os.path.exists(file_name), f"{file_name} non trovato!"
        assert os.path.getsize(file_name) > 0, f"{file_name} IS EMPTY!!"

        async with async_open(file_name, 'r') as json_file:
            json_files[json_file] = json.loads(await json_file.read())
    #  except when json files arent found


async def write_json():
    """
    Overwrites json files with the values in the dictionary storing its value every 5 minutes.
    """
    await asyncio.sleep(5*60)
    for file_name in json_files.keys():
        async with async_open(file_name, 'w+') as json_file:
            result = json.dumps(json_files[file_name], indent=4)
            await json_file.write(result)  # overwrite json with json_files values

            asyncio.create_task(write_json())  # repeats
            # questo modo di fare i loop non mi piace. lo riscriverò

