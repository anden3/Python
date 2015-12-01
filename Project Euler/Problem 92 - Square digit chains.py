from time import clock


def run_chain(limit):
    result = 0
    seen_nums = []
    win_cache = set()
    lose_cache = set()

    for n in range(1, limit):
        digit_square_sum = 0

        if n not in lose_cache:
            if n in win_cache:
                [win_cache.add(n) for n in seen_nums if n not in win_cache]
                seen_nums = []
                result += 1
            else:
                for c in str(n):
                    digit_square_sum += int(c) ** 2

                if digit_square_sum not in seen_nums:
                    seen_nums.append(digit_square_sum)
                else:
                    if digit_square_sum == 89:
                        [win_cache.add(n) for n in seen_nums if n not in win_cache]
                        seen_nums = []
                        result += 1
                    else:
                        [lose_cache.add(n) for n in seen_nums if n not in lose_cache]

    return result

t1 = clock()
print(run_chain(100000))
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
