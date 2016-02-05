from time import perf_counter


def coconuts(n):
    return (n ** n) - (n - 1)

t1 = perf_counter()
print(len(str(coconuts(50000))))
print(str((perf_counter() - t1) * 1000) + " ms.")
