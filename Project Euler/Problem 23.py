def div(n):
    return sum([x for x in range(1, n - 1) if n % x == 0])

print([z for z in range(1, 20001) if div(z) > z])