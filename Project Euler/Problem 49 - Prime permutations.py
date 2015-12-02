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


def prime_perm():
    for n in range(1000, 10000):
        prime_perms = list(sorted(set([int(''.join(p)) for p in permutations(str(n)) if isprime(int(''.join(p))) and str(''.join(p))[0] != "0"])))

        if len(prime_perms) >= 3:
            val1 = 0
            val2 = 0
            for perm in prime_perms:
                if val1 > 0:
                    if val2 - val1 == val1 - perm:
                        print(''.join([str(val2), str(val1), str(perm)]))
                        return 0

                    val2 = val1
                    val1 = perm
                else:
                    val1 = perm

t1 = clock()
prime_perm()
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")

