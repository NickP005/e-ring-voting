import hashlib
import math


"""
Class: Rng
Provides methods for generating random integers, bits, hexadecimal digits, and floating point numbers
by using the SHA256 cryptographic hash function.
Bits are returned as an integer [0,1].
Hexadecimal digits are returned as a string.
Once seeded, the random number generator will continue to produce random elements in a deterministic sequence.
"""
class Rng:

	def __init__(self,seed):
		self.state = seed.encode('utf-8')

	def init_rng(self,seed):
		self.state = seed.encode('utf-8')

	def random_int(self, lower_end=0, upper_end=100):
		range_length = upper_end - lower_end

		if(range_length != 1):
			num_digits = math.ceil(math.log(range_length,16)) #number of hex digits to generate


			valid = False
			random_int_string = ''

			while not valid: #loop until random number is in a valid range
				for digit in range(0,num_digits):
					random_int_string += self.random_hex()

				random_int_val = int(random_int_string,16) #convert the string to an integer value

				if(random_int_val < range_length): #is number in range?
					valid = True
				else:
					random_int_string = ''

			random_int_val = random_int_val + lower_end #adjust number to fit custom range
			return random_int_val
		else:
			return lower_end

	def random_float(self, lower_end=0, upper_end=1):
		float_str = '0.'

		for digit in range(17): #generate 17 random digits
			float_str += str(self.random_int(0,10))
		float_val = float(float_str) #get a number between 0 and 1

		range_length = upper_end - lower_end
		float_val = (float_val*range_length) + lower_end #adjust the number to fit custom range
		return float_val

	def random_bit(self):
		bit = self.random_int(0,16) % 2
		return bit

	def random_hex(self):
		hasher = hashlib.sha256()
		hasher.update(self.state)
		state = hasher.hexdigest()
		self.state = state.encode('utf-8') #use the hash digest as the next state
		hex_digit = state[:1] #use first digit as hex digit
		return hex_digit


"""
Class: Bitstream
Generates a sequence of random bits based on the seed value
"""
class Bitstream:

	def __init__(self, seed):
		self.rng = Rng(seed)

	def init_bitstream(self, seed):
		self.rng = Rng(seed)

	def next(self):
		next_bit = self.rng.random_bit()
		return next_bit


"""
Class: Floatstream
Generates a sequence of random floating point numbers based on the seed value
"""
class Floatstream:

	def __init__(self, seed, lower_end = 0, upper_end = 1):
		self.rng = Rng(seed)
		self.lower_end = lower_end
		self.upper_end = upper_end

	def init_floatstream(self, seed, lower_end = 0, upper_end = 1):
		self.rng = Rng(seed)
		self.lower_end = lower_end
		self.upper_end = upper_end

	def next(self):
		next_float = self.rng.random_float(self.lower_end, self.upper_end)
		return next_float


"""
Class: Intstream
Generates a sequence of random integers based on the seed value
"""
class Intstream:

	def __init__(self, seed, lower_end = 0, upper_end = 100):
		self.rng = Rng(seed)
		self.lower_end = lower_end
		self.upper_end = upper_end

	def init_intstream(self, seed, lower_end = 0, upper_end = 100):
		self.rng = Rng(seed)
		self.lower_end = lower_end
		self.upper_end = upper_end

	def next(self):
		next_int = self.rng.random_int(self.lower_end, self.upper_end)
		return next_int


"""
Class: Hexstream
Generates a sequence of random hexadecimal digits based on the seed value
"""
class Hexstream:

	def __init__(self, seed):
		self.rng = Rng(seed)

	def init_hexstream(self, seed):
		self.rng = Rng(seed)

	def next(self):
		next_hex = self.rng.random_hex()
		return next_hex
