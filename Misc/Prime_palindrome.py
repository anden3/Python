def palin(n):
    return str(n).casefold() == str(n)[::-1].casefold()


def is_prime(n):
    p = True
    for x in range(2, n):
        if n % x == 0:
            p = False
    if p:
        return True


def prime_palin(n):
    for x in range(n, 1000001):
        if palin(x) and is_prime(x):
            return x


print(prime_palin(50000))