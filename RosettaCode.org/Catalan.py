def cata(n):
    if n >= 0:
        return int((fact(n * 2)) / ((fact(n + 1)) * fact(n)))


def fact(n):
    n_sum = 1
    for x in range(2, n + 1):
        n_sum *= x
    return n_sum

for n in range(20):
    print(cata(n))