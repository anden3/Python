from time import clock


def is_pentagonal(n):
    return float((((24 * n + 1) ** 0.5) + 1.0) / 6.0).is_integer()


def penta_num():
    answers = []

    for x in range(1, 10000):
        for y in range(1, 10000):
            x_pent = x * (3 * x - 1) / 2
            y_pent = y * (3 * y - 1) / 2

            if is_pentagonal(x_pent) and is_pentagonal(y_pent):
                if is_pentagonal(x_pent + y_pent) and is_pentagonal(abs(x_pent - y_pent)):
                    answers.append(abs(x_pent - y_pent))

    return answers

t1 = clock()
print(penta_num())
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
