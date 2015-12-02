from functools import reduce
from time import clock


def sieve(limit):
    return reduce(lambda x, y: x - y, (set(range(x**2, limit, x)) for x in range(2, int(limit ** 0.5) + 1)), set(range(2, limit)))


def trun_prime(limit):
    trun_primes = []
    prime_list = sieve(limit)

    for n in range(10, limit):
        values = [n]
        all_primes = True

        [values.append(int(str(n)[0:x])) for x in range(1, len(str(n)))]
        [values.append(int(str(n)[x::])) for x in range(1, len(str(n)))]

        for x in values:
            if x not in prime_list:
                all_primes = False

        if all_primes:
            trun_primes.append(n)

    print(trun_primes)
    print(len(trun_primes))
    print(sum(trun_primes))

t1 = clock()
trun_prime(800000)
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
