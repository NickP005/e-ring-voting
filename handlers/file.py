import asyncio
import json
from aiofile import async_open
import os.path


json_files = {
    "data/settings.json":{},
    "data/known_nodes.json": {},
    "data/block_index.json": {}
}


async def load_dict():
    """
    Called when start_all. Loads json_files values.
    """
    global json_files
    for file_name in list(json_files):
        assert os.path.exists(file_name), f"{file_name} non trovato!"
        assert os.path.getsize(file_name) > 0, f"{file_name} IS EMPTY!!"

        async with async_open(file_name, 'r') as json_file:
            print("loading ", file_name, "...")
            file_content = await json_file.read()
            json_files[file_name] = json.loads(file_content)

    #  except when json files arent found


async def write_json():
    """
    Overwrites json files with the values in the dictionary storing its value every 5 minutes.
    """
    await asyncio.sleep(1)
    await asyncio.sleep(json_files["data/settings.json"]["file_update_interval"])
    print("Going to save local files..")
    for file_name in json_files.keys():
        print("saving ", file_name, "...")
        async with async_open(file_name, 'w+') as json_file:
            result = json.dumps(json_files[file_name], indent=4)
            await json_file.write(result)  # overwrite json with json_files values

    asyncio.create_task(write_json())  # repeats
            # questo modo di fare i loop non mi piace. lo riscriverò

#loads from memory the block bytes
async def loadBlockBytes(block_hash):
    file_name = "data/blocks/" + block_hash + ".voteblock"
    if not (os.path.exists(file_name) and os.path.getsize(file_name) > 0):
        print(f"Unable to load block bytes of {block_hash}")
        return False
    async with async_open(file_name, 'rb') as json_file:
        file_content = await json_file.read()
        return file_content
