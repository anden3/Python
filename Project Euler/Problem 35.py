from math import sqrt

lst = []


def is_prime(n):
    p = True
    for x in range(2, int(sqrt(n) + 1)):
        if n % x == 0:
            p = False
            break
    return p


def circ_prime(n):
    for x in range(2, n):
        p = True
        x_str = str(x)
        perms = [int(x_str[i:] + x_str[0:i]) for i in range(1, len(x_str))]
        for y in perms:
            if not is_prime(y):
                p = False
                break
        if p:
            lst.append(x)
    print(lst)

circ_prime(100000)