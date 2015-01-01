with open('names.txt') as f:
    names = f.read().split(',')
    names.sort()

sums = 0
pos = 0

for name in names:
    pos += 1
    for c in name.strip('"'):
        sums += (ord(c) - 64) * pos

print(sums)