nums = []


def substring(n):
    num = str(n)

    active_nums = []
    curr_num = 0

    for c in num:
        curr_num += int(c)
        active_nums.append(c)

        if curr_num == 10:
            num = num[1::]
            nums.append("".join(active_nums))
            substring(num)
        elif curr_num >= 10:
            num = num[1::]
            substring(num)


def substr_caller(n):
    for i in range(0, 10 ** n):
        substring(i)

substr_caller(5)
numSet = set(nums)
print(len(numSet))
