from math import sqrt


def prime(n):
    for x in range(2, n + 1):
        p = True
        for y in range(2, int(sqrt(x) + 1)):
                if x % y == 0:
                    p = False
                    break
        if p:
            print(x)

prime(100000)