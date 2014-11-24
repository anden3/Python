def prob():
    sums = 0
    for n in range(1000000):
        if str(n)[::1] == str(n)[::-1] and str(bin(n))[2::1] == str(bin(n))[:1:-1]:
            sums += n
    return sums

print(prob())