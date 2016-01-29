from time import perf_counter

max_degree = ("", 0)
words = open("../Words/english_words.txt").read().split()


def return_garland_degree(w):
    try:
        return max([len(w[:l]) for l in range(1, len(w) // 2 + 1) if w[:l] == w[-l:]])
    except ValueError:
        return 0

t1 = perf_counter()

for word in words:
    degree = return_garland_degree(word)

    if degree > max_degree[1]:
        max_degree = (word, degree)

print(max_degree)

print(str((perf_counter() - t1) * 1000) + " ms.")
