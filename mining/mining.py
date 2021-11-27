import hash
import hashlib
import random
import time
# from .file import json_files doesn't work

block_to_mine = b""
# miner address will be taken by the settings
miner_address_hex = "ead6ef03d61ee60c533d6d450c50a1e559a8a37f6b796a4094cd0dac6b744428"
#returns False if it has completed the iterations and doesn't have a block
# from is a random number from 0 to 2^64
def mine(iterations=1000000):
    start=random.randint(0, 2**61)
    difficulty = block_to_mine[64]
    print("difficulty", difficulty, " ", start)
    for i in range(iterations):
        nonce = (start + i).to_bytes(8, 'little')
        to_mine = block_to_mine + nonce
        block_hash = hashlib.sha256(to_mine).digest()
        #print(block_hash)
        if hash.hash_difficulty(block_hash) >= difficulty:
            print("FOUND BLOCK ----- with nonce ", (start + i))
            print("block hash", block_hash)
            print("successfully found block", block_to_mine + nonce)
            print(hash.hash_difficulty(block_hash))
            return block_to_mine + nonce
    return False

test_block = {}
test_block["pblockhash"] = hashlib.sha256("begula".encode()).hexdigest()
test_block["blocknum"] = 0
test_block["difficulty"] = 23
test_block["weight"] = 1
test_block["m_addr"] = hashlib.sha256("ghost".encode()).hexdigest()
test_block["transactions"] = []
test_block["nonce"] = 0

block_bytes = hash.from_json_to_bytes(test_block)
block_to_mine = block_bytes[:-8] #remove nonce for comodity


start_time = time.process_time()
found = False
while(not found):
    found = mine()
print("--- %s seconds ---" % (time.process_time() - start_time))
