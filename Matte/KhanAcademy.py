import sys


def func():
    for x in range(11, 100):
        for y in range(11, 100):
            if x - y == 21 and (x - 8) / (y - 8) == 4:
                print(x)
                print(y)
                sys.exit()

func()