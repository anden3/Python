from itertools import permutations
from time import clock


def isprime(n):
    n = abs(int(n))
    if n < 2:
        return False
    if n == 2:
        return True
    if not n & 1:
        return False
    for x in range(3, int(n**0.5) + 1, 2):
        if n % x == 0:
            return False
    return True


pan_list = []


def pandigital_primes(lim):
    test_str = []

    [test_str.append(str(x)) for x in range(1, lim + 1)]

    test_str = "".join(test_str)

    perms = [int(''.join(p)) for p in permutations(test_str)]

    temp_list = []

    [temp_list.append(perm) for perm in perms if isprime(perm)]

    if len(temp_list) > 0:
        pan_list.append(max(temp_list))

div_three_nums = [2, 3, 5, 6, 8, 9]

t1 = clock()
for num in range(9, 0, -1):
    if num not in div_three_nums:
        pandigital_primes(num)
print(max(pan_list))
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")