from time import time
from math import log


def get_log(line):
    num_arr = line.split(",")

    return log(float(num_arr[0])) * int(num_arr[1])

t1 = time()

file = open("base_exp.txt")
biggest_num = 0
current_line = 0

for l in file.readlines():
    current_line += 1
    if get_log(l) > biggest_num:
        biggest_num = get_log(l)
        maxline = current_line

print(biggest_num)
print(maxline)

t2 = time()

print(str((t2 - t1) * 1000) + "ms")