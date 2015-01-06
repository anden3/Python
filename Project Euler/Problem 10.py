from math import sqrt


def is_prime(n):
    p = True
    for x in range(2, int(sqrt(n) + 1)):
        if n % x == 0:
            p = False
    return p


def prob():
    n_sum = 0
    for n in range(2, 2000000):
        if is_prime(n):
            n_sum += n
    return n_sum

print(prob())