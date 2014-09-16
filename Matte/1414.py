import sys

n_list = []


def func():
    for x in range(0, 100):
        print(x)
        if 3**20 > 32**x:
            n_list.append(x)
    n_list.sort(reverse=True)
    print(n_list)
    sys.exit()

func()