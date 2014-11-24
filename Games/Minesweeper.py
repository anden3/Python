table = []


def make_table():
    x = int(input("Rows: "))
    y = int(input("Columns: "))

    for _ in range(x):
        table.append([["_"] * y], )


def print_table():
    for x in range(len(table)):
        for y in range(len(table[x])):
            print(" ".join(table[x][y]))

make_table()
table[0][1] = "X"
print(table)
print_table()