results = []

for n in range(0, 100):
    x = n / 100
    num2 = 0

    while num2 != x:
        num2 = x
        x = 4 * x * (1 - x)
        print(x)

    results.append(x)

print(results)
