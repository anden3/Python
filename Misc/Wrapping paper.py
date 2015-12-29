from math import pi


def paper_length(paper_width, tube, diameter):
    length = 0
    radius = (diameter - tube) / 2
    layers = radius // paper_width

    while layers > 0:
        length += diameter * pi
        layers -= 1
        diameter -= (paper_width * 2)

    return length / 1000

print(paper_length(0.05, 105, 265))
