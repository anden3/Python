from math import sqrt, floor
my_file = open("text.txt", "r+")


def f(n):
    my_file.write(str(floor(((1 + sqrt(5)) ** n - (1 - sqrt(5)) ** n) / (2 ** n * sqrt(5)))) + "\n")

for i in range(1, 1000):
    f(i)

my_file.close()