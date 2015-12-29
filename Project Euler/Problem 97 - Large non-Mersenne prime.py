from time import clock

t1 = clock()

large_num = 28433 * (2 ** 7830457) + 1

large_last = large_num % 10000000000

print(large_last)

t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
