bin_rows = [bin(0x000fb400)[2:].zfill(30), bin(0x371df39f)[2:].zfill(30), bin(0x145db7fb)[2:].zfill(30)]


def get_row(r, a):
    row = []
    for n in a:
        row.extend((bin_rows[r][9 - n], bin_rows[r][9 - n + 10], bin_rows[r][9 - n + 20]))
    return row


def print_num():
    input_numbers = [int(digit) for digit in list(input("What's the number?: "))]
    rows = [get_row(r, input_numbers) for r in range(3)]
    [print(''.join([(' ' if int(cell) == 0 else ('_' if i % 3 == 1 else '|')) for i, cell in enumerate(row)])) for row in rows]

print_num()
