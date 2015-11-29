from functools import reduce
from sys import setrecursionlimit
from time import clock

setrecursionlimit(20000)


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


def sieve(limit):
    return reduce(lambda x, y: x - y, (set(range(x**2, limit, x)) for x in range(2, int(limit ** 0.5) + 1)), set(range(2, limit)))

prime_list = sorted(list(sieve(3932)))


def prime_sum(lst):
    len_prime = len(lst)
    sum_prime = sum(lst)

    if sum_prime < 1000000:
        if isprime(sum_prime):
            print(sum_prime)
            print(len_prime)
            print(max(lst))
            return 0
        else:
            prime_sum(lst[1::])
    else:
        prime_sum(lst[:len_prime - 1:])


t1 = clock()
prime_sum(prime_list)
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
