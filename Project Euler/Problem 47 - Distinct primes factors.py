from functools import reduce
from time import clock


def sieve(limit):
    return reduce(lambda x, y: x - y, (set(range(x**2, limit, x)) for x in range(2, int(limit ** 0.5) + 1)), set(range(2, limit)))

prime_list = sorted(list(sieve(1000000)))


def distinct_prime_divisors(n):
    if n not in prime_list:
        while n > 1:
            for prime in prime_list:
                if prime <= n ** 0.5:
                    if n % prime == 0:
                        n /= prime
                        divisors.add(prime)
                        distinct_prime_divisors(n)
                else:
                    return divisors
    else:
        divisors.add(int(n))
        return divisors


t1 = clock()
prev1 = 0
prev2 = 0
prev3 = 0

for d in range(100000, 200000):
    divisors = set()
    if prev1 == prev2 == prev3 == len(distinct_prime_divisors(d)) == 4:
        print(d)
    else:
        prev3 = prev2
        prev2 = prev1
        prev1 = len(distinct_prime_divisors(d))

t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
