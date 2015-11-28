from functools import reduce
from time import clock


def sieve(limit):
    return reduce(lambda x, y: x - y, (set(range(x**2, limit, x)) for x in range(2, int(limit ** 0.5) + 1)), set(range(2, limit)))

prime_list = sieve(1000000)
circ_list = set()


def circ_primes():
    remove_list = []

    [remove_list.append(clean(n)) for n in prime_list if clean(n) != 0]

    map(prime_list.remove, remove_list)

    [recursive(n) for n in prime_list]

    print(len(circ_list))


def clean(n):
    num = n
    while num > 0:
        d = num % 10

        if d % 2 == 0 or d == 5:
            return n

        num /= 10
    return 0


def recursive(n):
    rots = set()

    [rots.add(str(n)[x:] + str(n)[:x]) for x in range(len(str(n)))]

    all_primes = True
    temp_list = []

    for rot in rots:
        rot = int(rot)

        if rot in prime_list:
            temp_list.append(rot)
        else:
            all_primes = False

    if all_primes:
        [circ_list.add(x) for x in temp_list]

t1 = clock()
circ_primes()
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
