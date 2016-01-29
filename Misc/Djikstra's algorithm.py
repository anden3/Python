from time import perf_counter

height, width = 17, 17

goal_found = False

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


def empty_array(w, h, c):
    return [[c for _ in range(w)] for _ in range(h)]


def list_to_set(arr):
    return set([(x, y) for x in range(len(arr[0])) for y in range(len(arr))])

node_distances = empty_array(width, height, width * height)
neighbors = empty_array(width, height, [])
unvisited_nodes = list_to_set(board)


def add_neighbors(diagonal):
    if diagonal:
        for y in range(height):
            y_vals = [y + n for n in [-1, 0, 1] if 0 <= y + n < height]

            for x in range(width):
                x_vals = [x + n for n in [-1, 0, 1] if 0 <= x + n < width]

                neighbors[y][x] = [(nx, ny) for nx in x_vals for ny in y_vals if (nx, ny) != (x, y)]
    else:
        for y in range(height):
            for x in range(width):
                neighbors[y][x] = [(nx, ny) for nx, ny in [(x + vx, y + vy) for vx in [-1, 0, 1] for vy in [-1, 0, 1] if abs(vx) != abs(vy) and 0 <= x + vx < width and 0 <= y + vy < height]]


def check_neighbors(node):
    global goal_found
    x, y = node

    if goal_found or node not in unvisited_nodes or board[y][x] == 1:
        return

    node_dist = int(node_distances[y][x])

    for nx, ny in neighbors[y][x]:
        if board[ny][nx] != 1 and node_dist + 1 < node_distances[ny][nx]:
            node_distances[ny][nx] = node_dist + 1

    unvisited_nodes.discard(node)

    if node == goal:
        goal_found = True

    for cx, cy in neighbors[y][x]:
        if (cx, cy) != node:
            check_neighbors((cx, cy))


def djikstra(initial, g, diagonal=False):
    global goal
    goal = g

    node_distances[initial[1]][initial[0]] = 0

    add_neighbors(diagonal)
    check_neighbors(initial)
    get_shortest_path()

    for y, row in enumerate(node_distances):
        print(' '.join([n if n == '.' else ('#' if board[y][x] == 1 else ' ') for x, n in enumerate(row)]))


def get_shortest_path():
    path = [goal]
    pos = goal

    while True:
        smallest_num = height * width
        smallest_pos = None

        for nx, ny in neighbors[pos[1]][pos[0]]:
            if node_distances[ny][nx] < smallest_num:
                smallest_pos = (nx, ny)
                smallest_num = node_distances[ny][nx]

        if smallest_pos is not None:
            path.append(smallest_pos)
            pos = smallest_pos

        if smallest_num == 0:
            break

    for x, y in path:
        node_distances[y][x] = "."

t1 = perf_counter()
djikstra((0, 0), (16, 16), diagonal=False)
print(str((perf_counter() - t1) * 1000) + " ms.")