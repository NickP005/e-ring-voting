import asyncio
import hashlib
import random
import time
import itertools
import psutil
import threading
import sys
import multiprocessing
from handlers.file import json_files
from mining import hash, block
from aiofile import async_open

sys.tracebacklimit = 0

block_to_mine = b""
hash_to_mine = b"" #actually is the hash of the block that has to be mined
#assigned transactions from a dedicated function which recovers not gone throught txs
assigned_transactions = []
# miner address will be taken by the settings
miner_address = b""
miner_address_hex = ""

found_nonces = {} #block_hash: nonce|None
do_mine = True #if False destroys the spaner() thread
#returns False if it has completed the iterations and doesn't have a block
# from is a random number from 0 to 2^64
def mine(difficulty, hash_to_mine, iterations=100000):
    start=random.randint(0, 2**61)
    #difficulty = block_to_mine[64]
    #print("difficulty", difficulty, " ", start)
    #global hash_to_mine
    #if len(hash_to_mine) != 32:
    #    print("no hash to mine present")
    #hash_to_mine = hashlib.sha256(block_to_mine).digest()
    for _ in itertools.repeat(None, iterations):
        start += 1 #7% impact!!
        nonce = start.to_bytes(8, 'little')
        #nonce = (lambda n:bytearray(map(random.getrandbits,(8,)*n)))(8)
        #to_mine =
        block_hash = hashlib.sha256(hash_to_mine + nonce).digest()
        #print(block_hash)
        if hash.hash_difficulty(block_hash) >= difficulty:
            #print("FOUND BLOCK ----- with nonce ", (start ))
            #print("block hash", block_hash)
            #print("successfully found block", hash_to_mine + nonce)
            #print( hash.hash_difficulty(block_hash))
            return hash_to_mine + nonce
    return False


async def start_mining():
    #load mining information from settings
    settings_file = json_files["data/settings.json"]
    miner_address_hex = settings_file["miner_address"]
    if len(miner_address_hex) != 64:
        print("Cannot proceed to start mining: the miner address is incorrect len!=64")
        return False
    miner_address = bytes.fromhex(miner_address_hex)
    #Now get how many cores we have. Minimum 2 for mining
    many_cores = psutil.cpu_count()
    print("cores:", many_cores)
    if(many_cores < 2):
        print("Cannot proceed to start mining: minimum cores requirement for mining is 2.")
        return False
    print("generating default block (just for testing!!)")
    await generateBlockToMine() #await defaultBlock()
    print(block_to_mine)
    await asyncio.sleep(1)
    try:
        threading.Thread(target=spawner).start()
    except KeyboardInterrupt:
        return True
    global do_mine
    while(do_mine):
        #here we update every 5 seconds the block to mine
        await asyncio.sleep(5)
        if(hash_to_mine.hex() in found_nonces):
            nonce_bytes = found_nonces[hash_to_mine.hex()]
            print("probably found a block!", len(nonce_bytes))
            bhash = hashlib.sha256(hash_to_mine + nonce_bytes).digest()
            print("recovered bhash", bhash.hex())
            print("block hash",hash_to_mine.hex())

            print("block to mine", block_to_mine)
            final_block = block_to_mine + nonce_bytes
            """
            async with async_open(hash_to_mine.hex() + ".voteblock", 'wb') as json_file:
                await json_file.write(final_block)"""

    #global do_mine
    #do_mine = False #to stop the mining thread

async def defaultBlock():
    test_block = {}
    test_block["pblockhash"] = hashlib.sha256("begula".encode()).hexdigest()
    test_block["blocknum"] = 0
    test_block["difficulty"] = 23
    test_block["weight"] = 1
    test_block["m_addr"] = hashlib.sha256("ghost".encode()).hexdigest()
    test_block["transactions"] = []
    test_block["epoch"] = 1639389055
    test_block["nonce"] = 0
    global block_to_mine
    block_bytes = hash.from_json_to_bytes(test_block)
    block_to_mine = block_bytes[:-8] #remove nonce for comodity
    global hash_to_mine
    if len(hash_to_mine) != 32:
        print("no hash to mine present")
        hash_to_mine = hashlib.sha256(block_to_mine).digest()
        print("default block hash", hash_to_mine.hex())

async def generateBlockToMine():
    block_cache = {}
    #first of all get the latest block
    while block.latest_block_hash == b"":
        print("mining.py: waiting for tree map")
        await asyncio.sleep(2)
    block_cache["pblockhash"] = block.latest_block_hash.hex()
    block_cache["blocknum"] = block.latest_block_number + 1
    block_cache["difficulty"] = block.latest_block_difficulty
    if block.median_time_blocks > 90:
        block_cache["difficulty"] += -1
    elif block.median_time_blocks < 30:
        block_cache["difficulty"] += 1
    block_cache["weight"] = block.latest_block_weight
    block_cache["m_addr"] = json_files["data/settings.json"]["miner_address"]

    #FOR NOW KEEP TRANSACTION THING NOT WORKING
    #the transactions every time there is a block update get erased and checked again
    block_cache["transactions"] = assigned_transactions

    print("block time", time.time())
    block_cache["epoch"] = int(time.time())
    block_cache["nonce"] = 0
    global block_to_mine
    block_bytes = hash.from_json_to_bytes(block_cache)
    block_to_mine = block_bytes[:-8] #remove nonce for comodity
    global hash_to_mine
    hash_to_mine = hashlib.sha256(block_to_mine).digest()
    print("generated block hash", hash_to_mine.hex())


def spawner():
    try:
        global do_mine
        print("spawner ", hash_to_mine)
        difficulty = block_to_mine[64]
        while(do_mine):
            manager = multiprocessing.Manager()
            return_dict = manager.dict()
            workers = []
            for i in range(psutil.cpu_count() - 1):
                p = multiprocessing.Process(target=worker, args=(i, return_dict, hash_to_mine, difficulty))
                workers.append(p)
                p.start()
            for proc in workers:
                proc.join()
            for proc in workers:
                proc.terminate()
            found_block = False
            block_found = b""
            for result in return_dict.values():
                if result is False:
                    do_mine = False
                    break
                if result is not None:
                    found_block = True
                    block_found = result
                    break
            if(found_block):
                print("FOUND BLOCK HASH ", block_found)
                #print("len of found hash", len(block_found))
                found_nonces[hash_to_mine.hex()] = block_found[-8:]
                print("FOUND NONCE ", found_nonces[hash_to_mine.hex()])
            #print(return_dict)
        print("spawner() process stopped")
    except KeyboardInterrupt:
        print("keyboard interrupt spawner()")
        do_mine = False
        return True

# https://www.youtube.com/watch?v=GK2GUxOnjDQ
def worker(procnum, return_dict, hash_to_mine, difficulty):
    try:
        result = mine(difficulty, hash_to_mine)
        if(result == False):
            return_dict[procnum] = None
        else:
            return_dict[procnum] = result
    except KeyboardInterrupt:
        return_dict[procnum] = False
        print ("Keyboard interrupt in process: ", procnum)
        return




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
