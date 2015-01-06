from math import sqrt


def is_prime(n):
    p = True
    for x in range(2, int(sqrt(n) + 1)):
        if n % x == 0:
            p = False
            break
    return p

print(is_prime(336790031231))