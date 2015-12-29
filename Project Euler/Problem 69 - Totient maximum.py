from functools import reduce
from time import clock


def sieve(limit):
    return reduce(lambda x, y: x - y, (set(range(x**2, limit, x)) for x in range(2, int(limit ** 0.5) + 1)), set(range(2, limit)))

prime_list = sorted(list(sieve(100000)))


def max_phi_num(limit):
    total = 1
    i = 0
    while total < limit - prime_list[i] * total:
        total *= prime_list[i]
        i += 1
    return total

t1 = clock()
print(max_phi_num(1000000))
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")