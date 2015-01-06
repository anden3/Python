from math import sqrt


def prime(n):
    lst = []
    for y in range(2, n + 1):
        p = True
        for x in range(2, int(sqrt(y))):
            if y % x == 0:
                p = False
        if p:
            lst.append(y)
    return lst


def p_fact(n):
    largest_num = 0
    for x in prime(10000):
        if n % x == 0 and x > largest_num:
            largest_num = x
    print(largest_num)

p_fact(600851475143)