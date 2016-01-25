from time import perf_counter


def gcd(a, b):
    if a % b != 0:
        return gcd(b, a % b)
    else:
        return b


def lcm(a, b):
    return abs(a * b) // gcd(a, b)


def add_fractions(a, b):
    if a[1] != b[1]:
        new_lower = lcm(a[1], b[1])
        a = (a[0] * (new_lower // a[1]), new_lower)
        b = (b[0] * (new_lower // b[1]), new_lower)

    return (a[0] + b[0]) // gcd(a[0] + b[0], a[1]), a[1] // gcd(a[0] + b[0], a[1])


def add_fractions_list(lst):
    total = (0, 1)

    for fraction in lst:
        total = add_fractions(total, fraction)

    return str(total[0]) + "/" + str(total[1])

t1 = perf_counter()
print(add_fractions_list([(1, 7), (35, 192), (61, 124), (90, 31), (5, 168), (31, 51), (69, 179), (32, 5), (15, 188), (10, 17)]))
print(str((perf_counter() - t1) * 1000) + " ms.")
