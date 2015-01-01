num = [0]
length = [0]
best_num = [0]
best_length = [0]


def collatz(n):
    if length[0] == 0:
        num[0] = n
    if n == 1:
        length[0] += 1
        if length[0] > best_length[0]:
            best_length[0] = length[0]
            length[0] = 0
            best_num[0] = num[0]
        else:
            length[0] = 0
        return
    if n % 2 == 0:
        length[0] += 1
        collatz(n / 2)
    elif n % 2 != 0:
        length[0] += 1
        collatz(n * 3 + 1)

for x in range(1, 1000000):
    collatz(x)

print('best num = ' + str(best_num[0]))
print('best length = ' + str(best_length[0]))