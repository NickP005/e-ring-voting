import hashlib

# this function is just demonstrative and probably used not so often
def hash_json_block(block_json):
    block_bytes = from_json_to_bytes(block_json)
    if block_bytes is False:
        print("something went wrong while computing the block hash")
        return False
    block_hash = hashlib.sha256(block_bytes)
    return block_hash.digest()

def from_json_to_bytes(block):
    try:
        if len(block["pblockhash"]) != 64 or len(block["pblockhash"]) != 64:
            return False
        previous_block_hash = bytes.fromhex(block["pblockhash"]) #32 bytes hash
        block_num = block["blocknum"].to_bytes(32, 'little')  #32 bytes number
        block_diff = block["difficulty"].to_bytes(1, 'little') #1 byte number
        block_weight = block["weight"].to_bytes(32, 'little') #32 bytes number
        transactions = txs_json_to_bytes(block["transactions"])
        miner_address = bytes.fromhex(block["m_addr"]) #sha256 miner address 32 bytes
        block_nonce = block["nonce"].to_bytes(8, 'little') #8 bytes number
        #this still needs block_hash
        blob = previous_block_hash + block_num + block_diff + block_weight + transactions + miner_address + block_nonce
        return blob
    except KeyError as e:
        print(f"this block miss {e}")
        return False

# this function specifically DOESN'T validate
def txs_json_to_bytes(transactions):
    #first of all tell everybody how many transactions they should expect
    many_transactions = len(transactions).to_bytes(2, 'little') # up to 65,535 txs
    blob = many_transactions

    #then for each transaction..
    for transaction in transactions:
        sender = bytes.fromhex(transaction["sender"])
        #now we have to tell how many receivers we have
        many_receivers = len(transaction["receiver"]).to_bytes(1, 'little') # up to 256
        transaction_blob = sender + many_receivers
        for receiver in transaction["receiver"]:
            receiver_addr = bytes.fromhex(receiver["addr"]) #32 bytes
            receiver_amount = receiver["amount"].to_bytes(4, 'little') #4 bytes = 16M each time
            transaction_blob = transaction_blob + receiver_addr + receiver_amount
        # now we have to put the signature (from hex of course)
        # the size depends on the signature. On verify stage along with the sender
        # amount, there will be also the sender's signature scheme and thus the size
        signature = bytes.fromhex(transaction["signature"])
        signature_size = len(signature) # size in bytes
        transaction_blob = transaction_blob + signature_size + signature
        blob = blob + transaction_blob
    return blob

def generateBlob():
    pass

#this needs to be higly optimized
def hash_difficulty(hash_bin):
    leading_zeros = 0
    for byte in hash_bin:
        leading_zeros += 8 - byte.bit_length()
        if byte.bit_length() != 0:
            break
    return leading_zeros

test_block = {}
test_block["pblockhash"] = hashlib.sha256("begula".encode()).hexdigest()
test_block["blocknum"] = 0
test_block["difficulty"] = 2
test_block["weight"] = 1
test_block["m_addr"] = hashlib.sha256("ghost".encode()).hexdigest()
test_block["transactions"] = []
test_block["nonce"] = 69420 #this nonce has 1 difficolty
test_block["bhash"] = "4dcf58cc4d60317da3220bf2807a2f01d8fcd7ad97bd4e10cd6da437fa00527d"


hashed = hash_json_block(test_block)
print(hashed)
print(hash_difficulty(hashed))
