import itertools
import time


def sub_str_div():
    start_str = "1234567890"
    answers = []

    perms = [''.join(p) for p in itertools.permutations(start_str)]

    for perm in perms:
        if perm[0] != "0" and perm[5] == "5":
            if int(perm[1:4]) % 2 == 0:
                if int(perm[2:5]) % 3 == 0:
                    if int(perm[3:6]) % 5 == 0:
                        if int(perm[4:7]) % 7 == 0:
                            if int(perm[5:8]) % 11 == 0:
                                if int(perm[6:9]) % 13 == 0:
                                    if int(perm[7::]) % 17 == 0:
                                        answers.append(int(perm))

    print(sum(answers))

t1 = time.clock()
sub_str_div()
t2 = time.clock()

print(str((t2 - t1) * 1000) + "ms")
