import asyncio
from hashlib import sha256
from handlers.file import json_files
from handlers import file, message
from mining import hash
# latest_block_hash will be obtained by the init function
latest_block_hash = b""
latest_block_weight = 0
latest_block_number = 0
latest_block_difficulty = 20
median_time_blocks = 60

block_hashes_chain = []

async def init():
    print("Going to initialize the blockchain..")
    print("mapping all the known blocks")
    global latest_block_hash, latest_block_weight, latest_block_number, latest_block_difficulty, median_time_blocks, block_hashes_chain
    chain, latest_block_weight = await mapTree(json_files["data/block_index.json"]["blocks"], json_files["data/settings.json"]["genesis_block"])
    latest_block_hash = bytes.fromhex(chain[-1])
    latest_block_number = len(chain) - 1
    block_hashes_chain = chain
    print("latest in-memory block:", latest_block_hash.hex())
    #here we should verify that each block of that chain is correct
    result = await verifyBlocks(chain)
    if not result:
        print("Unable to assure theese blocks are authentic. ", result)
    #now we have the longest chain and we have verified it
    #now we should calculate the average time of the last 11 blocks of the chain
    median_time_blocks = await getMedianTimeFrom(chain)
    latest_block_difficulty = await getBlockDifficulty(await file.loadBlockBytes(chain[-1]))
    print("median time of the latest blocks:", median_time_blocks)

async def mapTree(block_indexes, first_block):
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
            keep_searching = False
        outer_blocks = return_blocks.copy()
        used_blocks = {}
    #now calculate the weight of each chain
    chain_weights = {} # block_hash : weight
    for block_hash in outer_blocks:
        if block_hash not in chain_weights:
            chain_weights[block_hash] = 0
        for bhash in outer_blocks[block_hash]:
            chain_weights[block_hash] += 2 ** block_indexes[bhash]["difficulty"]
    #now get the biggest chain ever
    max_hash = ""
    max_weight = 0
    for block_hash, weight in chain_weights.items():
        if weight > max_weight:
            max_hash = block_hash
            max_weight = weight
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
        difficulty = await getBlockDifficulty(result)
        print("difficulty", difficulty)
        mhash = sha256(recovered_block_hash + result[-8:]).digest()
        if not (hash.hash_difficulty(mhash) >= difficulty):
            print("invalid difficulty of block ", block_hash)
            return False
        if recovered_block_hash.hex() == json_files["data/settings.json"]["genesis_block"]:
            #skip steps genesis block would fail
            continue
        if bytes.fromhex(block_index[block_hash]["prev"]) != result[:32]:
            print("Previous block hashes don't correspond")
            return False
        #I think there are more verifications idk I don't remember

    return True

# this function is called when we receive a block update
# both from our local mining and the network
# so here happens ALL the validation
async def blockUpdate(block_bytes, conn_nonce):
    # first of all we check if the previous blocks is in our latest 50 blocks
    update_blocks = block_hashes_chain[-50:]
    previous_hash_hex = await getBlockPrevious(block_bytes, 'hex')
    if previous_hash_hex not in update_blocks:
        print(f"Cannot append received block {conn_bytes} since has not previous")
        return False
    # now we check if the block number is correct based on the previous
    previous_block = file.loadBlockBytes(previous_hash_hex)
    previous_height = await getBlockHeight(previous_block, 'int')
    if await getBlockHeight(block_bytes, 'int') != (previous_height + 1):
        print("block.py: invalid block height")
        return False
    median_list_check = block_hashes_chain[block_hashes_chain.index(previous_hash_hex) - 12 : block_hashes_chain.index(previous_hash_hex)]
    print("len median list check", len(median_list_check))
    median_time = await getMedianTimeFrom(median_list_check)
    previous_block_difficulty = await getBlockDifficulty(previous_block)
    if(median_time > 90):
        previous_block_difficulty += 1
    elif(median_time < 30):
        previous_block_difficulty += -1
    if(previous_block_difficulty != (await getBlockDifficulty(block_bytes))):
        print(f"Cannot append received block {conn_bytes} since the difficulty is invalid")
        return False

async def getMedianTimeFrom(hash_chain):
    #get the last 11 blocks
    latest_chain = hash_chain[-12:]
    block_time_chain = []
    for block_hash in latest_chain:
        block_bytes = await file.loadBlockBytes(block_hash)
        block_time_chain.append(await getBlockEpoch(block_bytes, 'int'))
    if len(block_time_chain) < 3:
        return 60 #idk why its just the perfect block time
    latest_epoch_time = 0
    interval_arr = []
    for epoch_time in block_time_chain:
        if latest_epoch_time == 0:
            latest_epoch_time = epoch_time
            continue
        interval_arr.append(epoch_time - latest_epoch_time)
        latest_epoch_time = epoch_time
    return median(interval_arr)

async def getBlockPrevious(block_bytes, mode='bytes'):
    if mode == 'bytes':
        return block_bytes[:32]
    elif mode == 'hex':
        return block_bytes[:32].hex()

async def getBlockHeight(block_bytes, mode='bytes'):
    if mode == 'bytes':
        return block_bytes[32:64]
    elif mode == 'int':
        return int.from_bytes(block_bytes[32:64], "little")

async def getBlockEpoch(block_bytes, mode='bytes'):
    if mode == 'bytes':
        return block_bytes[-16:-8]
    elif mode == 'int':
        return int.from_bytes(block_bytes[-16:-8], "little")

async def getBlockDifficulty(block_bytes):
    return block_bytes[64]

async def median(lst):
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2

    if (lstLen % 2):
        return sortedLst[index]
    else:
        return (sortedLst[index] + sortedLst[index + 1])/2.0
