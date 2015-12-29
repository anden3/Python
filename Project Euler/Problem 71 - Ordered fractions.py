from fractions import Fraction
from time import clock


def gcd(a, b):
    if a % b != 0:
        return gcd(b, a % b)
    else:
        return b


def ordered_fractions(limit):
    for d in range(limit):
        show_next = False
        for n in range(d):
            if gcd(n, d) == 1:
                if show_next:
                    print([n, d, Fraction(n / d)])
                    show_next = False
                if Fraction(n / d) == Fraction(3 / 7):
                    show_next = True

t1 = clock()
ordered_fractions(8)
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
