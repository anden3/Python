from time import perf_counter


def sad_cycle(base, num):
    path = []
    cycle = set()

    while num != 1:
        if num > 9:
            new_num = 0

            for digit in list(str(num)):
                new_num += int(digit) ** base
            num = new_num
        else:
            num **= base

        if num in path:
            if num in cycle:
                break
            else:
                cycle.add(num)

        path.append(num)

    print(', '.join([str(n) for n in cycle]))

t1 = perf_counter()
sad_cycle(11, 2)
print(str((perf_counter() - t1) * 1000) + " ms.")
