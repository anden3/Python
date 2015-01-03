import itertools

num = 0
for x in itertools.permutations(range(10)):
    num += 1
    if num == 1000000:
        print(x)