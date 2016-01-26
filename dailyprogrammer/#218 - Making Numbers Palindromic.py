from time import perf_counter

lychrel_numbers = [196, 295, 394, 493, 592, 689, 691, 788, 790, 879, 887, 978, 986, 1495, 1497, 1585, 1587, 1675, 1677, 1765, 1767, 1855, 1857, 1945, 1947, 1997, 2494]
results = []
most_cycles = [0, 0, 0]


def make_palindrome(n):
    global most_cycles

    n0 = n
    cycles = 0

    if n in results or n in lychrel_numbers:
        return

    while list(str(n)) != list(str(n))[::-1]:
        cycles += 1

        n += int(''.join(list(str(n))[::-1]))

        if cycles > 1000:
            if cycles > most_cycles[2]:
                most_cycles = [n0, n, cycles]
            return

        if n in results:
            return

    if cycles > most_cycles[2]:
        most_cycles = [n0, n, cycles]

    return n


def check_palindromes():
    for n in range(10000):
        make_palindrome(n)
        results.append(n)
        print(n)

    print('{} gets palindromic after {}: {}'.format(most_cycles[0], str(most_cycles[2]) + " step" if most_cycles[2] == 1 else str(most_cycles[2]) + " steps", most_cycles[1]))


t1 = perf_counter()

check_palindromes()

print(str((perf_counter() - t1) * 1000) + " ms.")
