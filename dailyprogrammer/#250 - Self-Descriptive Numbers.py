from time import perf_counter

input_range = 7
results = []

t1 = perf_counter()


def sum_digits3(n):
    r = 0
    while n:
        r, n = r + n % 10, n // 10
    return r


def is_self_describing(n):
    num = str(n)

    if len(num) == sum_digits3(n):
        for c in range(len(num)):
            if num.count(str(c)) != int(num[c]):
                return False
        return True
    else:
        return False

print([i for i in range(10 ** (input_range - 1), 10 ** input_range, 10) if is_self_describing(i)])
print("Time taken: " + str((perf_counter() - t1) * 1000) + " ms.")
