from time import clock


def largest_digital_sum(limit):
    largest_sum = 0

    for a in range(limit):
        for b in range(limit):
            num_sum = sum(map(int, str(a**b)))

            if num_sum > largest_sum:
                largest_sum = num_sum

    return largest_sum

t1 = clock()
print(largest_digital_sum(100))
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")