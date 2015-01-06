primes = [2]


def prime(n):
    for x in range(2, n + 1):
        p = True
        for y in primes:
            if x % y == 0:
                p = False
        if p:
            primes.append(x)
    print(primes)

prime(100000)