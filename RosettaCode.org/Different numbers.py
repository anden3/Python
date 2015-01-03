def div(n):
    return sum([x for x in range(1, n - 1) if n % x == 0])

print('Deficient: ' + str(len([x for x in range(1, 20001) if div(x) < x])))
print('Perfect: ' + str(len([y for y in range(1, 20001) if div(y) == y])))
print('Abundant: ' + str(len([z for z in range(1, 20001) if div(z) > z])))