numbers = []


def func(num):
    num_sum = 0
    num = str(num)
    for n in num:
        num_sum += int(n) ** 5
    if num_sum == int(num):
        numbers.append(int(num))

for x in range(100000):
    func(x)

print(sum(numbers))