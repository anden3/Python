from time import clock

from PIL import Image, ImageDraw


def rule_90(row):
    new_row = [0]
    new_row += [1 if row[x - 1] != row[x + 1] else 0 for x in range(1, len(row) - 1)]
    new_row.append(0)

    return new_row


def rule_30(row):
    new_row = [0]

    for x in range(1, len(row) - 1):
        left = row[x - 1]
        middle = row[x]
        right = row[x + 1]
        value_sum = left + middle + right

        if value_sum == 0 or value_sum == 3:
            new_row.append(0)
        elif value_sum == 1:
            new_row.append(1)
        elif value_sum == 2 and left == 0:
            new_row.append(1)
        else:
            new_row.append(0)
    new_row.append(0)

    return new_row


def automata(steps):
    row = [0 for _ in range(steps)]
    row.append(1)
    row += [0 for _ in range(steps)]

    image = Image.new('RGB', (steps * 2 + 1 if steps >= 100 else 201, steps if steps >= 100 else 100), color=(255, 255, 255))
    width_step = round(image.size[0] / len(row))
    height_step = round(image.size[1] / steps)

    drawing = ImageDraw.Draw(image)

    # print(''.join(str(n) for n in row).replace("0", " ").replace("1", "#"))

    for x in range(steps):
        row = rule_30(row)
        for c in range(len(row)):
            if row[c] == 1:
                drawing.rectangle([c * width_step, x * height_step, (c + 1) * width_step, (x + 1) * height_step], fill=(0, 0, 0))

        # print(''.join(str(n) for n in row).replace("0", " ").replace("1", "#"))

    image.show()

t1 = clock()
automata(15)
t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
