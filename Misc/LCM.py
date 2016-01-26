def gcd(a, b):
    if a % b != 0:
        return gcd(b, a % b)
    else:
        return b


def lcm(a, b):
    return abs(a * b) // gcd(a, b)
