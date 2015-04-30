from math import sqrt


def div(n):
    return [x for x in range(2, int(sqrt(n)) + 1) if n % x == 0]

print(div(358482142))