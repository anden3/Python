import math
from time import clock

words = {
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",

    20: "twenty",
    30: "thirty",
    40: "forty",
    50: "fifty",
    60: "sixty",
    70: "seventy",
    80: "eighty",
    90: "ninety"
}

totalLetters = 0


def num_to_words(num):
    if num <= 20:
        return words[num]
    elif num < 100:
        word = words[math.floor(num / 10) * 10]

        if num % 10 != 0:
            word += words[int(str(num)[1::])]
        return word
    elif num < 1000:
        word = words[int(str(num)[0:1])]
        word += "hundred"

        if num % 100 != 0:
            if int(str(num)[1::]) < 20:
                word += "and"
                word += words[int(str(num)[1::])]
            else:
                if int(str(num)[1:2]) != 0:
                    word += "and"
                    word += words[math.floor(int(str(num)[1::]) / 10) * 10]
                if num % 10 != 0:
                    if "and" not in word:
                        word += "and"
                    word += words[int(str(num)[2::])]
        return word
    elif num < 10000:
        word = words[int(str(num)[0:1])]
        word += "thousand"

        if num % 1000 != 0:
            if int(str(num)[1:2]) != 0:
                word += words[int(str(num)[1:2])]
                word += "hundred"
            if num % 100 != 0:
                if int(str(num)[2::]) < 20:
                    word += "and"
                    word += words[int(str(num)[2::])]
                else:
                    if int(str(num)[2:3]) != 0:
                        word += "and"
                        word += words[math.floor(int(str(num)[2::]) / 10) * 10]
                    if num % 10 != 0:
                        if "and" not in word:
                            word += "and"
                        word += words[int(str(num)[3::])]
        return word

t1 = clock()
for x in range(1, 1001):
    totalLetters += len(num_to_words(x))
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
print(totalLetters)
