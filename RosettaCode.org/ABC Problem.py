blocks = [['B', 'O'], ['X', 'K'], ['D', 'Q'], ['C', 'P'], ['N', 'A'], ['G', 'T'], ['R', 'E'], ['T', 'G'], ['Q',
                                                                                                            'D'],
          ['F', 'S'], ['J', 'W'], ['H', 'U'], ['V', 'I'], ['A', 'N'], ['O', 'B'], ['E', 'R'], ['F', 'S'], ['L', 'Y'],
          ['P', 'C'], ['Z', 'M']]


def can_make_word(s):
    word = list(s)
    print(word)
    for char in word:
        for block in blocks:
            if char in block:
                blocks.remove(block)
                if len(word) > 0:
                    can_make_word(s[1::])
                else:
                    return

can_make_word('BARK')