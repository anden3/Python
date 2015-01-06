from math import sqrt

num = [0]


def is_prime(n):
    p = True
    for x in range(2, int(sqrt(n) + 1)):
        if n % x == 0:
            p = False
    return p


for y in range(2, 1000000):
    if is_prime(y):
        num[0] += 1
        if num[0] == 10001:
            print(y)
            break