from functools import reduce
from time import clock


def sieve(limit):
    return reduce(lambda x, y: x - y, (set(range(x**2, limit, x)) for x in range(2, int(limit ** 0.5) + 1)), set(range(2, limit)))

prime_list = list(sieve(10000))


def is_double_square(n):
    return float((n / 2.0) ** 0.5).is_integer()


def goldbach(limit):
    for n in range(3, limit, 2):
        if n not in prime_list:
            found_val = False
            for prime in prime_list:
                if n >= prime:
                    if is_double_square(n - prime):
                        found_val = True
                        break
            if not found_val:
                print(n)


t1 = clock()
goldbach(10000)
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
