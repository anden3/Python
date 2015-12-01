from time import clock


def is_palindrome(n):
    return str(n) == str(n)[::-1]


def lychrel_nums():
    count = 0

    for n in range(10000):
        num = n
        palindrome = False
        for x in range(50):
            num += int(str(num)[::-1])

            if is_palindrome(num):
                palindrome = True
        if not palindrome:
            count += 1
    return count

t1 = clock()
print(lychrel_nums())
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
