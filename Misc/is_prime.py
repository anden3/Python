def is_prime(n):
    p = True
    for x in range(2, n):
        if n % x == 0:
            p = False
    if p:
        return True