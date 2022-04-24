import asyncio
import hashlib
import random
import time
import psutil
import threading
import multiprocessing
from handlers.file import json_files
import hash
from mining import Block


class Mining:
    block_to_mine = b""
    hash_to_mine = b""  # actually is the hash of the block that has to be mined
    assigned_transactions = []  # assigned transactions from a dedicated function which recovers not gone through txs
    miner_address = b""  # miner address will be taken by the settings
    miner_address_hex = ""
    found_nonces = {}  # block_hash: nonce|None
    do_mine = True  # if False destroys the spawner() thread

    async def init(self):
        settings_file = json_files["data/settings.json"]

        miner_address_hex = settings_file["miner_address"]
        if len(miner_address_hex) != 64:
            print("Cannot proceed to start mining: the miner address is incorrect len!=64")
            return False

        # Now get how many cores we have. Minimum 2 for mining
        cpu_count = psutil.cpu_count()
        print("cores:", cpu_count)
        if cpu_count < 2:
            print("Cannot proceed to start mining: minimum cores requirement for mining is 2.")
            return False

        await self.generate_block()  # await defaultBlock()
        await asyncio.sleep(1)

        try:
            threading.Thread(target=Multiprocessing).start()
        except KeyboardInterrupt:
            return True

        while self.do_mine:
            """update every 5 seconds the block to mine"""
            await asyncio.sleep(5)
            if self.hash_to_mine.hex() in self.found_nonces:
                nonce_bytes = self.found_nonces[self.hash_to_mine.hex()]
                print("probably found a block!", len(nonce_bytes))
                bhash = hashlib.sha256(self.hash_to_mine + nonce_bytes).digest()
                print("recovered bhash", bhash.hex())
                print("block hash", self.hash_to_mine.hex())
                print("block to mine", self.block_to_mine)
                final_block = self.block_to_mine + nonce_bytes
                print("final block", final_block)

    async def generate_block(self):
        # first get the latest block
        while not Block.latest_block_hash:
            print("mining.py: waiting for tree map")
            await asyncio.sleep(2)
        block_cache = {
            "pblockhash": Block.latest_block_hash.hex(),
            "blocknum": Block.latest_block_number + 1,
            "difficulty": Block.latest_block_difficulty,
            "weight": Block.latest_block_weight,
            "m_addr": json_files["data/settings.json"]["miner_address"],
            "transactions": self.assigned_transactions,  # not working: gets erased and checked again every block update
            "epoch": int(time.time()),
            "nonce": 0
        }
        print("block time", time.time())

        if Block.median_time_blocks > 90:
            block_cache["difficulty"] -= 1
        elif Block.median_time_blocks < 30:
            block_cache["difficulty"] += 1

        block_bytes = hash.from_json_to_bytes(block_cache)
        self.block_to_mine = block_bytes[:-8]  # remove nonce for commodity
        self.hash_to_mine = hashlib.sha256(self.block_to_mine).digest()
        print("generated block hash", self.hash_to_mine.hex())

    async def default_block(self):
        test_block = {
            "pblockhash": hashlib.sha256("begula".encode()).hexdigest(),
            "blocknum": 0,
            "difficulty": 23,
            "weight": 1,
            "m_addr": hashlib.sha256("ghost".encode()).hexdigest(),
            "transactions": [],
            "epoch": 1639389055,
            "nonce": 0
        }
        block_bytes = hash.from_json_to_bytes(test_block)
        self.block_to_mine = block_bytes[:-8]  # remove nonce for commodity
        if len(self.hash_to_mine) != 32:
            print("no hash to mine present")
            self.hash_to_mine = hashlib.sha256(self.block_to_mine).digest()
            print("default block hash", self.hash_to_mine.hex())


class Multiprocessing:
    def __init__(self, hash_to_mine):
        self.hash_to_mine = hash_to_mine
        try:
            print("spawner ", hash_to_mine)
            self.difficulty = Mining.block_to_mine[64]
            while Mining.do_mine:
                manager = multiprocessing.Manager()
                return_dict = manager.dict()
                processes = []
                for i in range(psutil.cpu_count() - 1):
                    p = multiprocessing.Process(target=self.process, args=(i, return_dict))
                    processes.append(p)
                    p.start()
                for proc in processes:
                    proc.join()
                for proc in processes:  # ???
                    proc.terminate()
                for block_found in return_dict.values():
                    if not block_found:
                        Mining.do_mine = False
                        break
                    print("FOUND BLOCK HASH ", block_found)
                    Mining.found_nonces[hash_to_mine.hex()] = block_found[-8:]
                    print("FOUND NONCE ", Mining.found_nonces[hash_to_mine.hex()])
                    break
                # print(return_dict)
            print("spawner() process stopped")
        except KeyboardInterrupt:
            print("keyboard interrupt spawner()")
            Mining.do_mine = False

    def process(self, proc_num, return_dict):
        try:
            result = self.mine()
            if not result:
                return_dict[proc_num] = None
            else:
                return_dict[proc_num] = result
        except KeyboardInterrupt:
            return_dict[proc_num] = False
            print("Keyboard interrupt in process: ", proc_num)
            return

    def mine(self, iterations=100000):
        start = random.randint(0, 2 ** 61)
        for i in range(start, start + iterations):
            nonce = i.to_bytes(8, 'little')
            block_hash = hashlib.sha256(self.hash_to_mine + nonce).digest()
            if hash.hash_difficulty(block_hash) >= self.difficulty:
                return self.hash_to_mine + nonce
        return False


"""
test_block = {}
test_block["pblockhash"] = hashlib.sha256("begula".encode()).hexdigest()
test_block["blocknum"] = 0
test_block["difficulty"] = 22
test_block["weight"] = 1
test_block["m_addr"] = hashlib.sha256("ghost".encode()).hexdigest()
test_block["transactions"] = []
test_block["nonce"] = 0

block_bytes = hash.from_json_to_bytes(test_block)
block_to_mine = block_bytes[:-8] #remove nonce for comodity


start_time = time.process_time()
found = False
hashes = 0
while(not found):
    found = mine()
    hashes += 100000
just_mining = (time.process_time() - start_time)
print("--- %s seconds ---" % just_mining)
print("hashes ", hashes)
print("estimated hashes ", 2**test_block["difficulty"])

start_time = time.process_time()
for i in range(hashes):
    block_hash = hashlib.sha256(block_to_mine).digest()
    #hashes += 1 7% impact!!
just_hashes = (time.process_time() - start_time)
print("--- %s seconds ---" % just_hashes)

print("the mining function took", (-1 + just_mining / just_hashes) * 100, "% more time")
"""
