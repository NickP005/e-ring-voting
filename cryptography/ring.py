#PUBLIC PARAMETERS
PUBLIC_p = 0xB10B8F96A080E01DDE92DE5EAE5D54EC52C99FBCFB06A3C69A6A9DCA52D23B616073E28675A23D189838EF1E2EE652C013ECB4AEA906112324975C3CD49B83BFACCBDD7D90C4BD7098488E9C219A73724EFFD6FAE5644738FAA31A4FF55BCCC0A151AF5F0DC8B4BD45BF37DF365C1A65E68CFDA76D4DA708DF1FB2BC2E4A4371
PUBLIC_gen = 0xA4D1CBD5C3FD34126765A442EFB99905F8104DD258AC507FD6406CFF14266D31266FEA1E5C41564B777E690F5504F213160217B4B01B886A5E91547F9E2749F4D7FBD7D3B9A92EE1909D0D2263F80A76A6A24C087A091F531DBF0A0169B6A28AD662A4D18E73AFA32D779D5918D08BC8858F4DCEF97C2A24855E6EEB22B3B2E5
PUBLIC_order = 0xF518AA8781A8DF278ABA4E7D64B7CB9D49462353
#END OF PUBLIC PARAMETERS

#sample data
import randomic
import math
import sys
#every cN, zN and order is 20 bytes long
#every A1, prime, public_key, PUBLIC_p and PUBLIC_gen is 128 bytes long

#encode/decode the signature
def encode_signature(sig_tuple):
    (A1, cN, zN) = sig_tuple
    A1_bytes = A1.to_bytes(128, 'big')
    # here we hope that len(cN) == len(zN)
    many_members = len(cN).to_bytes(2, 'big')
    cN_bytes = bytes()
    zN_bytes = bytes()
    for i in range(len(cN)):
        cN_bytes = cN_bytes + cN[i].to_bytes(20, 'big')
        zN_bytes = zN_bytes + zN[i].to_bytes(20, 'big')
    return A1_bytes + many_members + cN_bytes + zN_bytes

def decode_signature(bytes):
    A1 = int.from_bytes(bytes[0:128], byteorder='big')
    many_members = int.from_bytes(bytes[128:130], byteorder='big')
    cN = []
    zN = []
    for i in range(many_members):
        cN.append(int.from_bytes(bytes[130 + i*20 : 150 + i*20], byteorder='big'))
        zN.append(int.from_bytes(bytes[130 + many_members*20 + i*20 : 150 + many_members*20 + i*20], byteorder='big'))
    return (A1, cN, zN)

#encode/decode public keys list
def encode_public_keys(pub_keys):
    pub_keys_bytes = bytes()
    many_members = len(pub_keys).to_bytes(2, 'big')
    for i in range(len(pub_keys)):
        pub_keys_bytes = pub_keys_bytes + pub_keys[i].to_bytes(128, 'big')
    return many_members + pub_keys_bytes

def decode_public_keys(bytes):
    many_members = int.from_bytes(bytes[0:2], byteorder='big')
    pub_keys = []
    for i in range(many_members):
        pub_keys.append(int.from_bytes(bytes[2 + i*128 : 130 + i*128], byteorder='big'))
    return pub_keys

#encode/decode tag (topic+message(vote))
allowed_letters_encoding = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM0123456789 ,.;:-_<>+-*/|'=!?$€%&()"
def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier
def encode_tag(topic, message):
    if(len(topic) > 16*255): #i know its 256
        print("topic too much big")
        return False
    many_chunks = round_up(len(topic)/16)
    print("chunk bytes", many_chunks*8)
    topic_bytes = bytes()
    char_index = 1
    latest_bits = 0
    for letter in topic:
        position = allowed_letters_encoding.find(letter)
        if(position == -1):
            print("bad characters")
            return False
        four_bits = position
        if char_index % 2 == 0:
            print(latest_bits)
            print(latest_bits)
            latest_bits = latest_bits | four_bits
            print(latest_bits)
            topic_bytes = topic_bytes + latest_bits.to_bytes(1, 'big')
            char_index += 1
        else:
            latest_bits = four_bits << 4
            char_index += 1
    print(topic_bytes.hex())

encode_tag("Do you want pizza or pasta?", "pizza")
#START OF HASH FUNCTIONS
#takes in data and outputs a number that is in G
def hash_zero(data):
  random_int = randomic.Rng(data).random_int(0, PUBLIC_order)
  return pow(PUBLIC_gen, random_int, mod=PUBLIC_p)
#takes in data and outputs a number that is in G
def hash_one(data):
  random_int = randomic.Rng(data + b"1").random_int(0, PUBLIC_order)
  return pow(PUBLIC_gen, random_int, mod=PUBLIC_p)
#takes in data and outputs a number that is between (0)1 to PUBLIC_order
def hash_two(data):
  return randomic.Rng(data + b"2").random_int(1, PUBLIC_order)
#END OF HASH FUNCTIONS

#PUBLIC-PRIVATE KEPAIR GENERATION
def gen_private():
  #I know I should use some cryptographic random...
  return int(randrange(1,PUBLIC_order))
def gen_public(private_xi):
  return pow(PUBLIC_gen, private_xi, mod=PUBLIC_p)
#END OF PUBLIC-PRIVATE KEPAIR GENERATION

#SIGNATURE GENERATION
def sign_message(private_key, issue, pub_keys):
    pass

#END OF SIGNATURE GENERATION
