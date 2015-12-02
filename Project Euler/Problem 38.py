from time import clock


def pan_multi():
    answers = set()

    for c in range(9234, 9488):
        total = ""

        for n in range(1, 10):
            total += str(c * n)
            compare_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

            if len(total) == 9 and int(total) % 9 == 0:
                all_nums = True

                for x in total:
                    if x in compare_list:
                        compare_list.remove(x)
                    else:
                        all_nums = False

                if all_nums:
                    answers.add(total)
    print(max(answers))


t1 = clock()
pan_multi()
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
