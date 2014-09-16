import sys

n_sum = [0]
times = [0]


def func(n):
    print(n)
    if times[0] < 64:
        n_sum[0] += n * 2
        times[0] += 1
        func(n * 2)
    else:
        print(n / 2)
        print(n_sum[0])
        sys.exit()

func(1)