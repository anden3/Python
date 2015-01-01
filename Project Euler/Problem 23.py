def div(n):
    return sum([x for x in range(1, n - 1) if n % x == 0])

ab_num = ([n for n in range(150) if div(n) > n])

print(set([n for n in range(300) for x in ab_num for y in ab_num if x + y == n]))