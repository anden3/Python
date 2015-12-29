def game(n):
    if n == 1:
        print(n)
        return True

    if n % 3 == 0:
        print(str(n) + "\t0")
        game(int(n / 3))
    else:
        if (n + 1) % 3 == 0:
            print(str(n) + "\t+1")
            game(int((n + 1) / 3))
        else:
            print(str(n) + "\t-1")
            game(int((n - 1) / 3))

game(31337357)
