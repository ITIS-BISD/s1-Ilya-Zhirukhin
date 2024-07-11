from random import randint

def generate_code(classroom_id):
	return str(classroom_id) + '#' + ''.join([chr(65 + randint(0, 25)) for _ in range(8)])
