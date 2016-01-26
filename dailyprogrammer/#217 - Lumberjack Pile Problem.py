from time import perf_counter

file = open("#217 Input.txt")

height = width = int(file.readline())
logs = int(file.readline())

board = []

for row in file.readlines():
    for value in row.split():
        board.append(int(value))


def print_board():
    for y in range(height):
        print(' '.join([str(board[x + (height * y)]) for x in range(height)]))


def fill_logs(l):
    while l > 0:
        smallest_pile = min(board)
        pile_count = board.count(smallest_pile)
        indexes = [i for i, n in enumerate(board) if n == smallest_pile]

        if l >= pile_count:
            for i in indexes:
                board[i] += 1
            l -= pile_count
        else:
            for i in indexes[:l]:
                board[i] += 1
            return

    return

t1 = perf_counter()
fill_logs(logs)
print_board()
print(str((perf_counter() - t1) * 1000) + " ms.")
