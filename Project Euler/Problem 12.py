import sys


def factors(n):
    return set(x for tup in ([i, n // i]
                             for i in range(1, int(n ** 0.5) + 1) if n % i == 0) for x in tup)


def prob():
    number = 0
    for n in range(1, 1000000):
        number += n
        print(len(factors(number)))
        if len(factors(number)) > 500:
            print(number)
            sys.exit()

prob()