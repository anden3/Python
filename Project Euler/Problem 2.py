a, b, sums = 1, 1, 0
while b < 4000000:
    sums += [b if b % 2 == 0 else 0][0]
    a, b = b, a + b
print(sums)