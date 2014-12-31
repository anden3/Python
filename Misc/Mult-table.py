def multi(n):
    table = []

    for x in range(1, n + 1):
        table.append([])
        for y in range(1, n + 1):
            table[x - 1].append('\t' + str(y * x))
        print(" ".join(table[x - 1]))

multi(10)