def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return reduce(lambda x, y: x * y, range(n, 1, -1))
