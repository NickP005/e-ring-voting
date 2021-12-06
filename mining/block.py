import asyncio
from hashlib import sha256
from handlers.file import json_files
from handlers import file, message
from mining import hash
# latest_block_hash will be obtained by the init function
latest_block_hash = b""
latest_block_weight = 0

async def init():
    print("Going to initialize the blockchain..")
    print("mapping all the known blocks")
    chain, latest_block_weight = await mapTree(json_files["data/block_index.json"]["blocks"])
    latest_block_hash = bytes.fromhex(chain[-1])
    print("latest in-memory block:", latest_block_hash.hex())
    result = await verifyBlocks(chain)
    if not result:
        print("Unable to assure theese blocks are authentic. ")
    #here we should verify that each block of that chain is correct


async def mapTree(block_indexes, first_block="3870354a4f52c2c40263476c282ea6079182f31cc0ca34e2b76a6f6d8eadf36a"):
    block_index = block_indexes.copy() #since we are deleting things for being fast
    outer_blocks = {first_block:[first_block]} #block hash : [list of hashes]
    return_blocks = outer_blocks.copy() #the same one as above
    #0 used blocks means its outer. >0 means its just
    used_blocks = {} #block hash : int representing if that is an outer or not
    keep_searching = True
    while(keep_searching):
        for index_hash, index_data in block_index.items():
            if index_data["prev"] in outer_blocks:
                if index_data["prev"] not in used_blocks:
                    used_blocks[index_data["prev"]] = 0
                used_blocks[index_data["prev"]] += 1
                return_blocks[index_hash] = outer_blocks[index_data["prev"]].copy()
                return_blocks[index_hash].append(index_hash)
        for block_hash, many_used in used_blocks.items():
            if(many_used > 0):
                # this hash is not a outer block
                del return_blocks[block_hash]
                del block_index[block_hash]
        if not used_blocks:
            #print("finished searching")
            keep_searching = False
        outer_blocks = return_blocks.copy()
        used_blocks = {}
    #print("finished mapping block trees: ", return_blocks)
    #now calculate the weight of each chain
    chain_weights = {} # block_hash : weight
    for block_hash in outer_blocks:
        if block_hash not in chain_weights:
            chain_weights[block_hash] = 0
        for bhash in outer_blocks[block_hash]:
            chain_weights[block_hash] += 2 ** block_indexes[bhash]["difficulty"]
    #print("chain weights", chain_weights)
    #now get the biggest chain ever
    max_hash = ""
    max_weight = 0
    for block_hash, weight in chain_weights.items():
        if weight > max_weight:
            max_hash = block_hash
            max_weight = weight
    #print("winning hash chain", block_hash)
    return return_blocks[block_hash], max_weight

#hash_array is hex
async def verifyBlocks(hash_array):
    block_index = json_files["data/block_index.json"]["blocks"]
    for block_hash in hash_array:
        result = await file.loadBlockBytes(block_hash)
        if result is False:
            return False
        recovered_block_hash = sha256(result[:-8]).digest()
        print("recovered hash is", recovered_block_hash.hex())
        if not (block_hash == recovered_block_hash.hex()):
            print("Recovered block hash doesn't correspond. Corrupted block.")
            return False
        difficulty = result[64]
        print("difficulty", difficulty)
        mhash = sha256(recovered_block_hash + result[-8:]).digest()
        if not (hash.hash_difficulty(mhash) >= difficulty):
            print("invalid difficulty")
            return False
        if recovered_block_hash.hex() == "3870354a4f52c2c40263476c282ea6079182f31cc0ca34e2b76a6f6d8eadf36a":
            #skip steps this block would fail
            continue
        if bytes.fromhex(block_index[block_hash]["prev"]) != result[:32]:
            print("Previous block hashes don't correspond")
            return False
