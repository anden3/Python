def next_step(row):
    new_row = [0]

    new_row += [1 if row[x - 1] != row[x + 1] else 0 for x in range(1, len(row) - 1)]

    new_row.append(0)

    return new_row


def rule_90(steps, current_row):
    print(''.join(str(n) for n in current_row).replace("0", " ").replace("1", "#"))

    for x in range(steps):
        current_row = next_step(current_row)
        print(''.join(str(n) for n in current_row).replace("0", " ").replace("1", "#"))

rule_90(10, [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
