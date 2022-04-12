from random import randrange

#PUBLIC PARAMETERS
PUBLIC_p = 0xB10B8F96A080E01DDE92DE5EAE5D54EC52C99FBCFB06A3C69A6A9DCA52D23B616073E28675A23D189838EF1E2EE652C013ECB4AEA906112324975C3CD49B83BFACCBDD7D90C4BD7098488E9C219A73724EFFD6FAE5644738FAA31A4FF55BCCC0A151AF5F0DC8B4BD45BF37DF365C1A65E68CFDA76D4DA708DF1FB2BC2E4A4371
PUBLIC_gen = 0xA4D1CBD5C3FD34126765A442EFB99905F8104DD258AC507FD6406CFF14266D31266FEA1E5C41564B777E690F5504F213160217B4B01B886A5E91547F9E2749F4D7FBD7D3B9A92EE1909D0D2263F80A76A6A24C087A091F531DBF0A0169B6A28AD662A4D18E73AFA32D779D5918D08BC8858F4DCEF97C2A24855E6EEB22B3B2E5
PUBLIC_order = 0xF518AA8781A8DF278ABA4E7D64B7CB9D49462353
#END OF PUBLIC PARAMETERS
def gen_private():
  #I know I should use some cryptographic random...
  return int(randrange(1,PUBLIC_order))

def timereps(reps, func):
    from time import time
    start = time()
    for i in range(0, reps):
        func()
    end = time()
    return (end - start) / reps

def fast_exponentiation(x, y, p) :
    res = 1     # Initialize result

    # Update x if it is more
    # than or equal to p
    x = x % p

    if (x == 0) :
        return 0

    while (y > 0) :

        # If y is odd, multiply
        # x with result
        if ((y & 1) == 1) :
            res = (res * x) % p

        # y must be even now
        y = y >> 1      # y = y/2
        x = (x * x) % p

    return res

def testpower1():
  for i in range(1000):
    fast_exponentiation(PUBLIC_gen,gen_private(),PUBLIC_p)

#benchmark of pow() function
def testpower2():
  for i in range(1000):
    pow(PUBLIC_gen, gen_private(), PUBLIC_p)

print("time of testpower1", timereps(1, testpower1))
print("time of testpower2", timereps(1, testpower2))
