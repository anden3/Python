from math import sqrt
from decimal import Decimal


def is_prime(n):
    p = True
    for x in range(2, int(sqrt(n) + 1)):
        if n % x == 0:
            p = False
            break
    return p


def mers_prime(n):
    for x in range(2, n):
        if is_prime(x):
            print("{:.2E}".format(Decimal(2 ** x - 1)))

mers_prime(100000)