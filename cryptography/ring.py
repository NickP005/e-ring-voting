#PUBLIC PARAMETERS
PUBLIC_p = 0xB10B8F96A080E01DDE92DE5EAE5D54EC52C99FBCFB06A3C69A6A9DCA52D23B616073E28675A23D189838EF1E2EE652C013ECB4AEA906112324975C3CD49B83BFACCBDD7D90C4BD7098488E9C219A73724EFFD6FAE5644738FAA31A4FF55BCCC0A151AF5F0DC8B4BD45BF37DF365C1A65E68CFDA76D4DA708DF1FB2BC2E4A4371
PUBLIC_gen = 0xA4D1CBD5C3FD34126765A442EFB99905F8104DD258AC507FD6406CFF14266D31266FEA1E5C41564B777E690F5504F213160217B4B01B886A5E91547F9E2749F4D7FBD7D3B9A92EE1909D0D2263F80A76A6A24C087A091F531DBF0A0169B6A28AD662A4D18E73AFA32D779D5918D08BC8858F4DCEF97C2A24855E6EEB22B3B2E5
PUBLIC_order = 0xF518AA8781A8DF278ABA4E7D64B7CB9D49462353
#END OF PUBLIC PARAMETERS

#sample data
import randomic, utils
import math
import sys
from random import randrange
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
"""
#the message can be a vote (starts with $) or a transfer (starts with *) to another group
#with another key
def encode_tag(topic, message):
    if(len(topic) > 16*255): #i know its 256
        print("topic too much big")
        return False
    if(len(message) > 16): #i know its 256
        print("message too much big")
        return False
    many_chunks = int(round_up(len(topic)/16))
    print("chunk bytes", many_chunks*16)
    topic_bytes = bytes()
    for letter in topic:
        position = allowed_letters_encoding.find(letter)
        if(position == -1):
            print("bad characters")
            return False
        topic_bytes += position.to_bytes(1, 'big')
    for _ in range((many_chunks*16) - len(topic)):
        topic_bytes += (62).to_bytes(1, 'big')

    message_bytes = bytes()
    for letter in message:
        position = allowed_letters_encoding.find(letter)
        if(position == -1):
            print("bad characters")
            return False
        message_bytes += position.to_bytes(1, 'big')
    for _ in range(16 - len(message)):
        message_bytes += (62).to_bytes(1, 'big')

    return (topic_bytes + message_bytes)
encoded_tag = encode_tag("Do you want pizza or pasta?", "pizza")
"""
#returns the topic encoded in bytes and
#the hash can be calculated after with bytes
"""
most of this data is just for the voter, so they can read:
 - timestamp of the proposal
 - brief title of max 30 characters
 - description of the proposal
 - (optional) instruction about the votes
 - candidates (so what to put in the message)
 - attached documents hashes and their title(no more 30 char)
 - links where to direct download through http documents (through TOR!)
 - (optional) magnet link to download the docs (through TOR!)
"""
def encode_topic():
    pass

#START OF HASH FUNCTIONS
#takes in data and outputs a number that is in G
def hash_zero(data):
  random_int = randomic.Rng(data + (0).to_bytes(1, 'big')).random_int(0, PUBLIC_order)
  return pow(PUBLIC_gen, random_int, mod=PUBLIC_p)
#takes in data and outputs a number that is in G
def hash_one(data):
  random_int = randomic.Rng(data + (1).to_bytes(1, 'big')).random_int(0, PUBLIC_order)
  return pow(PUBLIC_gen, random_int, mod=PUBLIC_p)
#takes in data and outputs a number that is between (0)1 to PUBLIC_order
def hash_two(data):
  return randomic.Rng(data + (2).to_bytes(1, 'big')).random_int(1, PUBLIC_order)
#END OF HASH FUNCTIONS

#PUBLIC-PRIVATE KEPAIR GENERATION
def gen_private():
  #I know I should use some cryptographic random...
  return int(randrange(1,PUBLIC_order))
def gen_public(private_xi):
  return pow(PUBLIC_gen, private_xi, mod=PUBLIC_p)
#END OF PUBLIC-PRIVATE KEPAIR GENERATION

#START OF UTILS FUNCTIONS
def check_membership(number, order, p):
  result = pow(number, order%p, mod=p)
  if(result == 1):
    return True
  else:
    print("check membership failed:",result)
    return False
#END OF UTILS FUNCTIONS

#START OF SIGNATURE GENERATION
#position from 1 to len+1
def sign_message(private_key_num, issue_hash_bytes, message_bytes, pub_keys_bytes, position):
    h = hash_zero(issue_hash_bytes + pub_keys_bytes)
    sigma_i = pow(h, private_key_num, mod=PUBLIC_p)
    A0 = hash_one(issue_hash_bytes + pub_keys_bytes + message_bytes)
    A1 = pow(utils.getFractionModulo(sigma_i , A0), utils.getFractionModulo(1,position), PUBLIC_p)
    pub_keys = decode_public_keys(pub_keys_bytes)
    signature_list = []
    for j in range(1, len(pub_keys) + 1):
        if(j == position):
          signature_list.append(sigma_i)
          continue
        sigma_j = (A0 * (pow(A1, j, mod=PUBLIC_p))) % PUBLIC_p
        signature_list.append(sigma_j)
    randomw_i = gen_private()
    a_list = []
    b_list = []
    cj_list = []
    zj_list = []
    for j in range(1, len(pub_keys) + 1):
        if(j == position):
            a_list.append(pow(PUBLIC_gen, randomw_i, mod=PUBLIC_p))
            b_list.append(pow(h, randomw_i, mod=PUBLIC_p))
            cj_list.append(0)
            zj_list.append(0)
            continue
        z_j = gen_private()
        c_j = gen_private()
        cj_list.append(c_j)
        zj_list.append(z_j)
        a_j = (pow(PUBLIC_gen, z_j, mod=PUBLIC_p) * pow(pub_keys[j-1], c_j, mod=PUBLIC_p)) % PUBLIC_p
        b_j = (pow(h, z_j, mod=PUBLIC_p) * pow(signature_list[j-1], c_j, mod=PUBLIC_p)) % PUBLIC_p
        a_list.append(a_j)
        b_list.append(b_j)
    c_hash2 = hash_two(issue_hash_bytes + pub_keys_bytes + A0.to_bytes(128, 'big') + A1.to_bytes(128, 'big') + encode_public_keys(a_list) + encode_public_keys(b_list))
    sum_of_cj = 0
    for element in cj_list:
        sum_of_cj += element
    cj_list[(position-1)] = (c_hash2 - (sum_of_cj)) % PUBLIC_order
    zj_list[(position-1)] = (randomw_i - (cj_list[position-1] * private_key_num) % PUBLIC_order ) % PUBLIC_order
    return encode_signature((A1, cj_list, zj_list))
#END OF SIGNATURE GENERATION
#START OF SIGNATURE VERIFICATION
def check_signature(signature_bytes, issue_hash_bytes, message_bytes, pub_keys_bytes):
    (A1, cN, zN) = decode_signature(signature_bytes)
    if not check_membership(A1, PUBLIC_order, PUBLIC_p):
        print("A1 not of G")
        return False
    pub_keys = decode_public_keys(pub_keys_bytes)
    for pub_key in pub_keys:
        if not check_membership(pub_key, PUBLIC_order, PUBLIC_p):
          print(pub_key, "public key not of G")
          return False
    for ci in cN:
        if not (ci > 0 and ci < PUBLIC_order):
            print(ci, "ci not of G")
            print(cN)
            return False
    for zi in zN:
        if not (zi > 0 and zi < PUBLIC_order):
            print(zi, " zi not of G")
            print(zN)
            return False
    h = hash_zero(issue_hash_bytes + pub_keys_bytes)
    A0 = hash_one(issue_hash_bytes + pub_keys_bytes + message_bytes)
    signature_list = []
    for i in range(1, len(pub_keys)+1):
        sig = (A0 * (pow(A1, i, mod=PUBLIC_p))) % PUBLIC_p
        signature_list.append(sig)
    a_list = []
    b_list = []
    for i in range(len(pub_keys)):
        a1 = pow(PUBLIC_gen, zN[i], mod=PUBLIC_p)
        a2 = pow(pub_keys[i], cN[i], mod=PUBLIC_p)
        b1 = pow(h, zN[i], mod=PUBLIC_p)
        b2 = pow(signature_list[i], cN[i], mod=PUBLIC_p)
        a_list.append((a1*a2)%PUBLIC_p)
        b_list.append((b1*b2)%PUBLIC_p)
    c_hash2 = hash_two(issue_hash_bytes + pub_keys_bytes + A0.to_bytes(128, 'big') + A1.to_bytes(128, 'big') + encode_public_keys(a_list) + encode_public_keys(b_list))
    sum_of_cN = 0
    for element in cN:
        sum_of_cN += element
    if not (sum_of_cN % PUBLIC_order) == c_hash2:
        print("sum not equal. Signature invalid")
        return False
    return True

def trace_signatures(pub_keys_bytes, issue_hash_bytes, messages_bytes_array, signature_bytes_array):
    h = hash_zero(issue_hash_bytes + pub_keys_bytes)
    signatures = []
    many_members = int.from_bytes(pub_keys_bytes[0:2], byteorder='big')
    print("many members:", many_members)
    many_signatures = len(signature_bytes_array)
    for i in range(many_signatures):
        (A1,_,_) = decode_signature(signature_bytes_array[i])
        sigs = trace_get_sigs(messages_bytes_array[i], issue_hash_bytes + pub_keys_bytes, many_members, A1, h)
        signatures.append(sigs)
    many_duplicates = 0
    impostor = None
    for member_i in range(many_members):
        column_sigs = []
        for i in range(many_signatures):
            column_sigs.append(signatures[i][member_i])
        if len(column_sigs) != len(set(column_sigs)):
            many_duplicates += 1
            impostor = member_i
    if many_duplicates == 1:
        return (True, impostor)
        #to get the public just pub_keys_bytes[impostor]
    elif many_duplicates == many_members:
        #the signature is identical
        return (True, "linked")
    else:
        return (False, "indep")

def trace_get_sigs(message_bytes, tag_bytes, many_members, A1, h):
    A0 = hash_one(tag_bytes + message_bytes)
    signature_list = []
    for i in range(1, many_members+1):
        sig = (A0 * (pow(A1, i, mod=PUBLIC_p))) % PUBLIC_p
        signature_list.append(sig)
    return signature_list
#END OF SIGNATURE VERIFICATION


public_key_list = [];

our_private_key = gen_private()
our_public_key = gen_public(our_private_key)
public_key_list.append(our_public_key)

for i in range(11):
    private_key = gen_private()
    public_key_list.append(gen_public(private_key))

signature = sign_message(our_private_key, b"ttt", b"pasta", encode_public_keys(public_key_list), 1)
print("finished signing")
print(len(signature))

check = check_signature(signature, b"ttt", b"pasta", encode_public_keys(public_key_list))

print("check went", check)
signature2 = sign_message(our_private_key, b"ttt", b"pastaa", encode_public_keys(public_key_list), 1)
trace = trace_signatures(encode_public_keys(public_key_list), b"ttt", [b"pasta", b"pastaa"], [signature, signature2])

print("trace went", trace)
