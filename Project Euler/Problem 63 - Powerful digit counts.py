from math import ceil
from time import clock

t1 = clock()

lower = 0
result = 0
n = 1

while lower < 10:
    lower = ceil(10 ** ((n - 1.0) / n))
    result += 10 - lower
    n += 1

print(result)
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
