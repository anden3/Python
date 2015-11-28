from time import clock


def money(pounds):
    target_pence = pounds * 100
    ways = 0

    for a in range(target_pence, -1, -200):
        for b in range(a, -1, -100):
            for c in range(b, -1, -50):
                for d in range(c, -1, -20):
                    for e in range(d, -1, -10):
                        for f in range(e, -1, -5):
                            for g in range(f, -1, -2):
                                ways += 1

    print(ways)


t1 = clock()
money(2)
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
