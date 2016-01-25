import time

tri_nums = [1]

file = open("Words.txt")
words = file.read()
file.close()

words = words.translate({ord('"'): None})
words = words.split(",")


def triangle_num(n):
    [tri_nums.append(tri_nums[i] + (i + 2)) for i in range(n)]


def word_value(word):
    value = 0

    for c in word:
        value += ord(c) - ord('A') + 1

    return value

t1 = time.clock()
triangle_num(250)
count = 0

for w in words:
    if word_value(w) in tri_nums:
        count += 1

print(count)

t2 = time.clock()

print(str((t2 - t1) * 1000) + "ms")
