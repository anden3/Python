from time import perf_counter

from PIL import Image

board = [
    [0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0],
    [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0],
    [1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    [1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0],
    [0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
    [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

height, width = len(board), len(board[0])


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None
        self.H = 0
        self.G = 0

nodes = [[Node(x, y) for x in range(width)] for y in range(height)]

image = Image.open('maze.png')
pixels = list(image.getdata())
w, h = image.size
pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]
print(pixels)


def distance(node1, node2):
    return abs(node1.x - node2.x) + abs(node1.y - node2.y)


def get_neighbors(node, diagonal):
    if diagonal:
        y_vals = [node.y + n for n in [-1, 0, 1] if 0 <= node.y + n < height]
        x_vals = [node.x + n for n in [-1, 0, 1] if 0 <= node.x + n < width]

        return [nodes[ny][nx] for nx in x_vals for ny in y_vals if (nx, ny) != (node.x, node.y) and board[ny][nx] != 1]
    else:
        return [nodes[ny][nx] for nx, ny in [(node.x + vx, node.y + vy)
                                             for vx in [-1, 0, 1]
                                             for vy in [-1, 0, 1]
                                             if abs(vx) != abs(vy) and 0 <= node.x + vx < width and 0 <= node.y + vy < height and board[vy][vx] != 1]]


def draw_path(path):
    for x, y in path:
        board[y][x] = '.'

    for row in board:
        print(' '.join([n if n == '.' else ('#' if n == 1 else ' ') for n in row]))


def a_star(start, goal, diagonal=True):
    open_set = set()
    closed_set = set()

    current = start
    open_set.add(current)

    while open_set:
        current = min(open_set, key=lambda o: o.G + o.H)

        if current == goal:
            path = []

            while current.parent:
                path.append((current.x, current.y))
                current = current.parent

            path.append((current.x, current.y))
            draw_path(path[::-1])
            return

        open_set.remove(current)
        closed_set.add(current)

        for node in get_neighbors(current, diagonal):
            if node in closed_set:
                continue

            if node in open_set:
                new_g = current.G + 1

                if node.G > new_g:
                    node.G = new_g
                    node.parent = current
            else:
                node.G = current.G + 1
                node.H = distance(node, goal)
                node.parent = current
                open_set.add(node)

    raise ValueError('No Path Found')

t1 = perf_counter()
a_star(nodes[4][6], nodes[0][16])
print(str((perf_counter() - t1) * 1000) + " ms.")
