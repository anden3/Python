from time import clock


def is_triangular(n):
    return ((((8 * n + 1) ** 0.5) - 1.0) / 2.0).is_integer()


def is_pentagonal(n):
    return ((((24 * n + 1) ** 0.5) + 1.0) / 6.0).is_integer()


def find_num(limit):
    for n in range(2, limit):
        n_hex = n * (2 * n - 1)

        if is_pentagonal(n_hex) and is_triangular(n_hex) and n_hex > 40755:
            return n_hex

t1 = clock()
print(find_num(100000))
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
