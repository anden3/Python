file = open("#200 Input.txt")

line_1 = file.readline().split()
width = int(line_1[0])
height = int(line_1[1])

board = [list(file.readline().strip("\n")) for y in range(height)]

last_line = file.readline().split()

targets = {(int(last_line[1]), int(last_line[0]))}
fill_char = last_line[2]
replace_char = board[int(last_line[1])][int(last_line[0])]


def print_board():
    [print(''.join(row)) for row in board]


def flood_fill(torus=False):
    while len(targets) > 0:
        x, y = targets.pop()

        if board[x][y] == replace_char:
            board[x][y] = fill_char

            new_targets = []

            if not torus:
                if x > 0:
                    new_targets.append((x - 1, y))

                if x < height - 1:
                    new_targets.append((x + 1, y))

                if y > 0:
                    new_targets.append((x, y - 1))

                if y < width - 1:
                    new_targets.append((x, y + 1))
            else:
                if x > 0:
                    new_targets.append((x - 1, y))
                else:
                    new_targets.append((height - 1, y))

                if x < height - 1:
                    new_targets.append((x + 1, y))
                else:
                    new_targets.append((0, y))

                if y > 0:
                    new_targets.append((x, y - 1))
                else:
                    new_targets.append((x, width - 1))

                if y < width - 1:
                    new_targets.append((x, y + 1))
                else:
                    new_targets.append((x, 0))

            targets.update(new_targets)


print_board()
flood_fill(torus=True)
print()
print_board()

