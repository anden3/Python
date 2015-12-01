from time import clock

str_val = {
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'T': 10,
    'J': 11,
    'Q': 12,
    'K': 13,
    'A': 14
}


def royal_flush(values, suits):
    if values == [10, 11, 12, 13, 14] and len(set(suits)) == 1:
        return 914
    else:
        return False


def straight_flush(values, suits):
    if len(set(suits)) == 1:
        for x, y in zip(values, map(lambda i: i - 1, values[1:])):
            if x != y:
                return False
        return max(values) + 800
    else:
        return False


def four_of_a_kind(values):
    unique_values = sorted(list(set(values)))

    if len(unique_values) <= 2:
        for val in unique_values:
            elements = [n for n, x in enumerate(values) if x == val]

            if len(elements) == 4:
                return elements[0] + 700
        return False
    else:
        return False


def full_house(values):
    unique_values = sorted(list(set(values)))

    if len(unique_values) == 2:
        part_1 = [n for n, x in enumerate(values) if x == unique_values[0]]
        part_2 = [n for n, x in enumerate(values) if x == unique_values[1]]

        if (len(part_1) == 3 and len(part_2) == 2) or (len(part_1) == 2 and len(part_2) == 3):
            return part_1[0] + 600
        else:
            return False
    else:
        return False


def flush(suits):
    if len(set(suits)) == 1:
        return 500


def straight(values):
    for x, y in zip(values, map(lambda i: i - 1, values[1:])):
        if x != y:
            return False
    return max(values) + 400


def three_of_a_kind(values):
    unique_values = sorted(list(set(values)))

    if 2 <= len(unique_values) <= 3:
        for val in unique_values:
            elements = [n for n, x in enumerate(values) if x == val]

            if len(elements) == 3:
                return elements[0] + 300
        return False
    else:
        return False


def two_pairs(values):
    unique_values = sorted(list(set(values)))

    if 2 <= len(unique_values) <= 3:
        part_1 = [n for n, x in enumerate(values) if x == unique_values[0]]
        part_2 = [n for n, x in enumerate(values) if x == unique_values[1]]

        if (len(part_1) == 2 and len(part_2) == 2) or (len(part_1) == 2 and len(part_2) == 2):
            return part_1[0] + 200
        else:
            return False
    else:
        return False


def one_pair(values):
    unique_values = sorted(list(set(values)))

    if len(unique_values) <= 4:
        for val in unique_values:
            elements = [n for n, x in enumerate(values) if x == val]

            if len(elements) == 2:
                return elements[0] + 100
        return False
    else:
        return False


def high_card(values):
    return max(values)


def poker_value(hand):
    cards_value = sorted([int(str_val[c[0]]) for c in hand])
    cards_suit = [c[1] for c in hand]

    if not royal_flush(cards_value, cards_suit):
        if not straight_flush(cards_value, cards_suit):
            if not four_of_a_kind(cards_value):
                if not full_house(cards_value):
                    if not flush(cards_suit):
                        if not straight(cards_value):
                            if not three_of_a_kind(cards_value):
                                if not two_pairs(cards_value):
                                    if not one_pair(cards_value):
                                        return high_card(cards_value)
                                    else:
                                        return one_pair(cards_value)
                                else:
                                    return two_pairs(cards_value)
                            else:
                                return three_of_a_kind(cards_value)
                        else:
                            return straight(cards_value)
                    else:
                        return flush(cards_suit)
                else:
                    return full_house(cards_value)
            else:
                return four_of_a_kind(cards_value)
        else:
            return straight_flush(cards_value, cards_suit)
    else:
        return royal_flush(cards_value, cards_suit)


t1 = clock()

file = open("poker.txt")
lines = [l.strip('\n').translate({ord(' '): ord(',')}) for l in file.readlines()]
file.close()

p1_wins = 0
p2_wins = 0

for line in lines:
    p1_hand = line[0:14].split(',')
    p2_hand = line[15::].split(',')

    p1_val = poker_value(p1_hand)
    p2_val = poker_value(p2_hand)

    if p1_val == p2_val and 100 <= p1_val <= 200:
        p1_val = high_card(sorted([int(str_val[c[0]]) for c in p1_hand]))
        p2_val = high_card(sorted([int(str_val[c[0]]) for c in p2_hand]))

    if p1_val > p2_val:
        p1_wins += 1
    elif p1_val < p2_val:
        p2_wins += 1

print([p1_wins, p2_wins])

t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
