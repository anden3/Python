def palin(x):
    return x.casefold() == x[::-1].casefold()

print(palin(""))