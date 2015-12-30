from time import time


def div(n):
    count = 2
    i = 2

    while i ** 2 < n:
        if n % i == 0:
            count += 2
        i += 1

    count += (1 if i ** 2 == n else 0)
    return count

t1 = time()
print(div(981273921))
t2 = time()

print(str((t2 - t1) * 1000) + "ms")