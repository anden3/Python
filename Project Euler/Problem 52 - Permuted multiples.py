from time import clock


def perm_mult(limit):
    def sort(n):
        return sorted(str(n))

    for x in range(1, limit):
        if sort(x) == sort(x * 2) == sort(x * 3) == sort(x * 4) == sort(x * 5) == sort(x * 6):
            return x

t1 = clock()
print(perm_mult(1000000))
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
