def div(n):
    return sum([x for x in range(1, n - 1) if n % x == 0])

print(sum(set([n + div(n) for n in range(10000) if div(div(n)) == n and n != div(n)])))