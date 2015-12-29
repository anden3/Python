def gcd(a, b):
    if a % b != 0:
        return gcd(b, a % b)
    else:
        return b

print(gcd(1616, 864))
