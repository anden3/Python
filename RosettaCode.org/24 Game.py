import random


def r_num(): return random.randint(1, 9)

nums = [r_num() for _ in range(4)]
print(nums)

while len(nums) > 1:
    operator = input('Operator: ')
    if operator == '+':
        nums[0] += nums[1]
    elif operator == '-':
        nums[0] -= nums[1]
    elif operator == '*':
        nums[0] *= nums[1]
    elif operator == '/':
        nums[0] /= nums[1]
    nums.pop(1)
    print(nums)
else:
    if nums[0] == 24:
        print('You won!')
    else:
        print('Game Over!')