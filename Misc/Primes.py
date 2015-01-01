def prime(n):
    for y in range(2, n + 1):
        p = True
        for x in range(2, y):
            if y % x == 0:
                p = False
        if p:
            print(y)