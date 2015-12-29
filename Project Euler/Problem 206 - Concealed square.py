from time import clock


def match(i):
    s = str(i)
    return not all(int(s[x * 2]) == x + 1 for x in range(9))

n = 138902663

t1 = clock()

while match(n * n):
    n -= 2

print(n * 10)

t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
