from hashlib import sha256
from handlers.file import json_files
from handlers import file  # , message
import hash


class Block:
    latest_block_hash = b""  # will be obtained by the init function
    latest_block_weight = 0
    latest_block_number = 0
    latest_block_difficulty = 20
    median_time_blocks = 60
    block_hashes_chain = []

    def __init__(self):
        print("Going to initialize the blockchain..")
        print("mapping all the known blocks")
        self.chain, self.latest_block_weight = await self.map_tree(
            json_files["data/block_index.json"]["blocks"],
            json_files["data/settings.json"]["genesis_block"]
        )

    async def init(self):
        self.latest_block_hash = bytes.fromhex(self.chain[-1])
        self.latest_block_number = len(self.chain) - 1
        self.block_hashes_chain = self.chain
        print("latest in-memory block:", self.latest_block_hash.hex())

        # here we should verify that each block of that chain is correct
        result = await self.verify_blocks()
        if not result:
            print("Unable to assure theese blocks are authentic. ", result)

        # now we have the longest chain and we have verified it
        # now we should calculate the average time of the last 11 blocks of the chain
        self.median_time_blocks = await self.median_time()
        self.latest_block_difficulty = await self.difficulty(await file.loadBlockBytes(self.chain[-1]))
        print("median time of the latest blocks:", self.median_time_blocks)

    async def verify_blocks(self):
        block_index = json_files["data/block_index.json"]["blocks"]
        for block_hash in self.chain:
            result = await file.loadBlockBytes(block_hash)
            if not result:
                return False
            recovered_block_hash = sha256(result[:-8]).digest()
            print("recovered hash is", recovered_block_hash.hex())
            if not block_hash == recovered_block_hash.hex():
                print("Recovered block hash doesn't correspond. Corrupted block.")
                return False
            difficulty = await self.difficulty(result)
            print("difficulty", difficulty)
            mhash = sha256(recovered_block_hash + result[-8:]).digest()
            if hash.hash_difficulty(mhash) < difficulty:
                print("invalid difficulty of block ", block_hash)
                return False
            if recovered_block_hash.hex() == json_files["data/settings.json"]["genesis_block"]:
                # skip steps genesis block would fail
                continue
            if bytes.fromhex(block_index[block_hash]["prev"]) != result[:32]:
                print("Previous block hashes don't correspond")
                return False
            # I think there are more verifications IDK I don't remember

        return True

    async def median_time(self, hash_chain=None):
        if hash_chain is None:
            hash_chain = self.chain
        # get the last 11 blocks
        latest_chain = hash_chain[-12:]
        block_time_chain = []
        for block_hash in latest_chain:
            block_bytes = await file.loadBlockBytes(block_hash)
            block_time_chain.append(await self.epoch(block_bytes, 'int'))
        if len(block_time_chain) < 3:
            return 60  # idk why its just the perfect block time
        latest_epoch_time = 0
        interval_arr = []
        for epoch_time in block_time_chain:
            if latest_epoch_time == 0:
                latest_epoch_time = epoch_time
                continue
            interval_arr.append(epoch_time - latest_epoch_time)
            latest_epoch_time = epoch_time

        # median
        s = sorted(interval_arr)
        length = len(interval_arr)
        i = (length - 1) // 2
        return s[i] if length % 2 else (s[i] + s[i + 1]) / 2.0

    async def update(self, block_bytes):
        """
        this function is called when we receive a block update
        both from our local mining and the network
        so here happens ALL the validation
        """
        # first of all we check if the previous blocks is in our latest 50 blocks
        update_blocks = self.block_hashes_chain[-50:]
        previous_hash_hex = await self.previous(block_bytes, 'hex')
        if previous_hash_hex not in update_blocks:
            # print(f"Cannot append received block {conn_bytes} since has not previous")
            return False
        # now we check if the block number is correct based on the previous
        previous_block = await file.loadBlockBytes(previous_hash_hex)
        previous_height = await self.height(previous_block, 'int')
        if await self.height(block_bytes, 'int') != (previous_height + 1):
            print("block.py: invalid block height")
            return False
        median_list_check = self.block_hashes_chain[
                            self.block_hashes_chain.index(previous_hash_hex) - 12:
                            self.block_hashes_chain.index(previous_hash_hex)
                            ]
        print("len median list check", len(median_list_check))
        median_time = await self.median_time(median_list_check)
        previous_block_difficulty = await self.difficulty(previous_block)
        if median_time > 90:
            previous_block_difficulty += 1
        elif median_time < 30:
            previous_block_difficulty += -1
        if previous_block_difficulty != (await self.difficulty(block_bytes)):
            # print(f"Cannot append received block {conn_bytes} since the difficulty is invalid")
            return False

    @staticmethod
    async def map_tree(block_indexes, first_block):  # *MI FIDO DI QUELLO CHE HAI SCRITTO NON HO VOGLIA DI CAPIRE* -lin
        block_index = block_indexes.copy()  # since we are deleting things for being fast
        outer_blocks = {first_block: [first_block]}  # block hash : [list of hashes]
        return_blocks = outer_blocks.copy()  # the same one as above
        # 0 used blocks means its outer. >0 means its just
        used_blocks = {}  # block hash : int representing if that is an outer or not
        keep_searching = True
        while keep_searching:
            for index_hash, index_data in block_index.items():
                if index_data["prev"] in outer_blocks:
                    if index_data["prev"] not in used_blocks:
                        used_blocks[index_data["prev"]] = 0
                    used_blocks[index_data["prev"]] += 1
                    return_blocks[index_hash] = outer_blocks[index_data["prev"]].copy()
                    return_blocks[index_hash].append(index_hash)
            for block_hash, many_used in used_blocks.items():
                if many_used > 0:
                    # this hash is not an outer block
                    del return_blocks[block_hash]
                    del block_index[block_hash]
            if not used_blocks:
                keep_searching = False
            outer_blocks = return_blocks.copy()
            used_blocks = {}
        # now calculate the weight of each chain
        chain_weights = {}  # block_hash : weight
        for block_hash in outer_blocks:
            if block_hash not in chain_weights:
                chain_weights[block_hash] = 0
            for bhash in outer_blocks[block_hash]:
                chain_weights[block_hash] += 2 ** block_indexes[bhash]["difficulty"]
        # now get the biggest chain ever
        max_hash = ""
        max_weight = 0
        for block_hash, weight in chain_weights.items():
            if weight > max_weight:
                max_hash = block_hash
                max_weight = weight
        return return_blocks[max_hash], max_weight

    @staticmethod
    async def previous(block_bytes, mode='bytes'):
        if mode == 'bytes':
            return block_bytes[:32]
        elif mode == 'hex':
            return block_bytes[:32].hex()

    @staticmethod
    async def height(block_bytes, mode='bytes'):
        if mode == 'bytes':
            return block_bytes[32:64]
        elif mode == 'int':
            return int.from_bytes(block_bytes[32:64], "little")

    @staticmethod
    async def epoch(block_bytes, mode='bytes'):
        if mode == 'bytes':
            return block_bytes[-16:-8]
        elif mode == 'int':
            return int.from_bytes(block_bytes[-16:-8], "little")

    @staticmethod
    async def difficulty(block_bytes):
        return block_bytes[64]
