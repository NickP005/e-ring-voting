import hash
import hashlib
import random
import time
import itertools
# from .file import json_files doesn't work

block_to_mine = b""
# miner address will be taken by the settings
miner_address_hex = "ead6ef03d61ee60c533d6d450c50a1e559a8a37f6b796a4094cd0dac6b744428"
#returns False if it has completed the iterations and doesn't have a block
# from is a random number from 0 to 2^64
def mine(iterations=100000):
    start=random.randint(0, 2**61)
    difficulty = block_to_mine[64]
    print("difficulty", difficulty, " ", start)
    for _ in itertools.repeat(None, iterations):
        start += 1
        nonce = start.to_bytes(8, 'little')
        #nonce = (lambda n:bytearray(map(random.getrandbits,(8,)*n)))(8)
        #to_mine =
        block_hash = hashlib.sha256(block_to_mine + nonce).digest()
        #print(block_hash)
        if hash.hash_difficulty(block_hash) >= difficulty:
            print("FOUND BLOCK ----- with nonce ", (start ))
            print("block hash", block_hash)
            print("successfully found block", block_to_mine + nonce)
            print(hash.hash_difficulty(block_hash))
            return block_to_mine + nonce
    return False

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
    hashes += 1
just_hashes = (time.process_time() - start_time)
print("--- %s seconds ---" % just_hashes)

print("the mining function took", (-1 + just_mining / just_hashes) * 100, "% more time")
