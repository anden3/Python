import math


def is_prime(n):
    if n % 2 == 0 and n > 2:
        return False
    return all(n % i for i in range(3, int(math.sqrt(n)) + 1, 2))


def prob():
    n_sum = 0
    for n in range(2, 2000000):
        if is_prime(n):
            n_sum += n
    return n_sum

print(prob())