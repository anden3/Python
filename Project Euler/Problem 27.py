from time import clock

bestValues = [0, 0]
bestN = 0


def isprime(n):
    n = abs(int(n))
    if n < 2:
        return False
    if n == 2:
        return True
    if not n & 1:
        return False
    for x in range(3, int(n**0.5) + 1, 2):
        if n % x == 0:
            return False
    return True


def quad_primes(a, b):
    global bestN
    n = 0

    while isprime(n**2 + a * n + b):
        n += 1

    if n > bestN:
        bestValues[0] = a
        bestValues[1] = b
        bestN = n

t1 = clock()

for x in range(-1000, 1000):
    for y in range(-1000, 1000):
        quad_primes(x, y)

t2 = clock()

print(bestValues)
print(bestN)

print("Answer = " + str(bestValues[0] * bestValues[1]))

print(str((t2 - t1) * 1000) + "ms")
