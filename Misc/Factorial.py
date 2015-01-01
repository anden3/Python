def fact(n):
    n_sum = 1
    for x in range(2, n + 1):
        n_sum *= x
    return n_sum

print(fact(7))