from time import clock


def get_sides():
    p = {}
    result = 0

    for a in range(1, 999):
        for b in range(1, 1000 - a):
            for c in range(1, 10001 - b - a):
                if a * a + b * b == c * c:
                    p[a + b + c] += 1

    for i in range(len(p)):
        if p[i] > p[result]:
            result = i

    print(result)
    print(p[result])

t1 = clock()
get_sides()
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
