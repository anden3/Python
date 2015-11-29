from time import clock


def pandigital():
    answers = set()

    for x in range(2, 60):
        start = 1234 if x < 10 else 123
        for y in range(start, 10000 // x):
            product = x * y
            num_string = str(x) + str(y) + str(product)
            compare_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

            if len(num_string) == 9 and int(num_string) % 9 == 0:
                all_nums = True

                for c in num_string:
                    if c in compare_list:
                        compare_list.remove(c)
                    else:
                        all_nums = False

                if all_nums:
                    answers.add(product)

    print(sum(answers))

t1 = clock()
pandigital()
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
