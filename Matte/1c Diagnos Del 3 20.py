import sys
sys.setrecursionlimit(100000)

n = 1


def divide(num):
    global n
    print(n)
    for i in range(2, 10):
        if num % i != 0:
            n += 1
            divide(n)
    print("Answer is " + str(num))
    sys.exit()

divide(n)