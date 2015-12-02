from functools import reduce
from time import clock


def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return reduce(lambda x, y: x * y, range(n, 1, -1))


def combinations(n, r):
    return int((factorial(n)) / (factorial(r) * factorial(n - r)))


def mill_comb(limit):
    count = 0

    for n in range(1, limit + 1):
        for r in range(1, n + 1):
            if combinations(n, r) > 1000000:
                count += 1

    return count

t1 = clock()
print(mill_comb(100))
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
