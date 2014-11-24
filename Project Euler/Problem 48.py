def prob():
    n_sum = 0
    for n in range(1, 1001):
        n_sum += n ** n
    n_sum = str(n_sum)
    return n_sum[len(str(n_sum)) - 10:len(str(n_sum)):1]

print(prob())