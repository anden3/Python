import sys


def song(n):
    if n > 0:
        print(str(n) + ' bottles of beer on the wall')
        print(str(n) + ' bottles of beer')
        print('Take one down, pass it around')
        print(str(n - 1) + ' bottles of beer on the wall')
        print('')
        song(n - 1)
    else:
        sys.exit()

song(99)