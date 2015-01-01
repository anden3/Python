def palin(n):
    return str(n).casefold() == str(n)[::-1].casefold()

print(palin(800))