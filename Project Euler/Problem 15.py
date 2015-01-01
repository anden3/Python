def fact(n):
    n_sum = 1
    for x in range(2, n + 1):
        n_sum *= x
    return n_sum


def lattice(a, b):
    x = fact(a + b)
    y = fact(a)
    y **= 2
    return int(x / y)

print(lattice(20, 20))