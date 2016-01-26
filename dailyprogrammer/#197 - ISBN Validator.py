def validate2(isbn):
    numbers = isbn.replace('-', '')
    total = 0

    if len(numbers) != 10:
        return False

    for i, n in enumerate(list(numbers)):
        total += int(n) * (len(numbers) - i)

    if total % 11 != 0:
        return (total - int(numbers[-1]) + 10) % 11 == 0
    return True


def validate(isbn):
    return True if sum([int(n) * (len(isbn.replace('-', '')) - i) for i, n in enumerate(list(isbn.replace('-', '')))]) % 11 == 0 else (True if (sum([int(n) * (len(isbn.replace('-', '')) - i) for i, n in enumerate(list(isbn.replace('-', ''))[:-1])]) + 10) % 11 == 0 else False)

print(validate("0-7475-3269-9"))
