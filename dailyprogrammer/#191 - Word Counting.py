from collections import Counter


def parse_book(f):
    print(sorted(Counter([w.lower() for w in f.read().split()]).items(), key=lambda x: x[1], reverse=True))

parse_book(open("#191 Input.txt"))
