from collections import defaultdict
from time import clock


def connections(attempt):
    l = len(attempt)

    for i in range(l - 1):
        for j in range(i + 1, l):
            yield attempt[i], attempt[j]


def make_number_graph(filename):
    file = open(filename)
    lines = [line.strip("\n") for line in file.readlines()]
    file.close()

    graph = defaultdict(set)

    for attempt in lines:
        for a, b in connections(attempt):
            graph[int(a)].add(int(b))

    return return_pass(graph)


def return_pass(graph):
    password = ""

    for key in sorted(graph, key=lambda k: len(graph[k]), reverse=True):
        password += str(key)

    if len(list(graph[int(password[len(password) - 1:len(password)])])) >= 1:
        password += str(list(graph[int(password[len(password) - 1:len(password)])])[0])

    return password

t1 = clock()
print(make_number_graph("keylog.txt"))
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")