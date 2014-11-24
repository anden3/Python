def prob():
    sums = 0
    n_sum = 0
    for n in range(2, 2000000):
        for x in str(n)[::]:
            n_sum += int(x) ** 5
        if n_sum == n:
            sums += n_sum
        n_sum = 0
    return sums

print(prob())