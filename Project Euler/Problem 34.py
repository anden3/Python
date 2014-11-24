def prob():
    sums = 0
    for n in range(10, 1000000):
        y_sum = 0
        for x in str(n)[0:len(str(n)):1]:
            y_sum += frac(int(x))
        if y_sum == n:
            sums += y_sum
    return sums


def frac(x):
    x_sum = 1
    for y in range(int(x), 1, -1):
        x_sum *= y
    return x_sum

print(prob())