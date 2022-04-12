# Python3 implementation of the approach
m= 0xB10B8F96A080E01DDE92DE5EAE5D54EC52C99FBCFB06A3C69A6A9DCA52D23B616073E28675A23D189838EF1E2EE652C013ECB4AEA906112324975C3CD49B83BFACCBDD7D90C4BD7098488E9C219A73724EFFD6FAE5644738FAA31A4FF55BCCC0A151AF5F0DC8B4BD45BF37DF365C1A65E68CFDA76D4DA708DF1FB2BC2E4A4371

# Function to return the GCD
# of given numbers
def gcd(a, b):

    if (a == 0):
        return b
    return gcd(b % a, a)

# Recursive function to return (x ^ n) % m
def modexp(x, n):

    if (n == 0) :
        return 1

    elif (n % 2 == 0) :
        return modexp((x * x) % m, n // 2)

    else :
        return (x * modexp((x * x) % m,
                           (n - 1) / 2) % m)


# Function to return the fraction modulo mod
def getFractionModulo(a, b):

    c = gcd(a, b)

    a = a // c
    b = b // c

    # (b ^ m-2) % m
    ##d = modexp(b, m - 2)
    d = pow(b,m-2, m)
    # Final answer
    ##ans = ((a % m) * (d % m)) % m
    ans = ((a % m) * d) % m
    return ans

def getSubractionModulo(a,b):
  r = (a-b) % m

# Driver code
if __name__ == "__main__":

    a = 2
    b = 6

    print ( getFractionModulo(a, b))
