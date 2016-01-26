from math import floor, ceil

words = []
letters_dict = {}
letters = []
fixed_letters = {}

char_value = {
    'a': 1,
    'b': 3,
    'c': 8,
    'd': 1,
    'e': 1,
    'f': 3,
    'g': 2,
    'h': 3,
    'i': 1,
    'j': 7,
    'k': 3,
    'l': 2,
    'm': 3,
    'n': 1,
    'o': 2,
    'p': 4,
    'q': 0,
    'r': 1,
    's': 1,
    't': 1,
    'u': 4,
    'v': 3,
    'w': 0,
    'x': 8,
    'y': 7,
    'z': 8,
    'å': 4,
    'ä': 4,
    'ö': 4,

    'è': 0
}


def choose_dict(language='swedish'):
    if language == 'swedish':
        return open('../Words/swedish_words.txt', 'r').read().split('\n')
    else:
        return open('/usr/share/dict/Words', 'r').read().split('\n')


def get_letters():
    chars = list(input("What letters do you have?: ").replace(' ', '').lower())
    copy = chars.copy()

    for i, c in enumerate(copy):
        if c.isdigit():
            if i < len(copy) - 1 and copy[i + 1].isalpha():
                fixed_letters[int(c) - 1] = copy[i + 1]
                chars.remove(c)

            elif copy[i + 1] == '[':
                if copy.index(']', i + 1):
                    fixed_letters[int(c) - 1] = copy[i + 2:copy.index(']', i + 1)]
                    offset = len(copy) - len(chars)

                    for _ in range(chars.index(']') + 1):
                        chars.pop(i - offset)

            elif copy[i + 1] == '*':
                fixed_letters[int(c) - 1] = '*'
                chars.pop(i)

    return chars


def scan_words():
    fixed_matches = set(words)
    word_values = {}
    word_lists = []
    wild_cards = 0

    if len(fixed_letters) > 0:
        for char_index in fixed_letters:
            if isinstance(fixed_letters[char_index], list):
                word_lists.append(fixed_letters[char_index])

                for word in fixed_matches.copy():
                    if len(word) - 1 >= max(fixed_letters):
                        if word[char_index].lower() not in fixed_letters[char_index]:
                            fixed_matches.discard(word)
                    else:
                        fixed_matches.discard(word)

            elif fixed_letters[char_index] == '*':
                wild_cards += 1
            else:
                for word in fixed_matches.copy():
                    if len(word) - 1 >= max(fixed_letters):
                        if word[char_index].lower() != fixed_letters[char_index]:
                            fixed_matches.discard(word)
                    else:
                        fixed_matches.discard(word)

    if len(letters) > 0:
        for word in fixed_matches.copy():
            word_list_values = []
            wild_cards_local = wild_cards

            for letter in letters:
                letters_dict[letter] = True

            for _ in range(len(word_lists)):
                word_list_values.append(True)

            if len(word) > 0:
                for char in word.lower():
                    if char in letters and letters_dict.get(char, False):
                        letters_dict[char] = False

                    elif len(word_lists) > 0:
                        is_in_wordlist = False

                        for y in range(len(word_lists)):
                            for x in range(len(word_lists[y])):
                                if char in word_lists[y][x] and word_list_values[y]:
                                    word_list_values[y] = False
                                    is_in_wordlist = True

                        if not is_in_wordlist and wild_cards_local <= 0:
                            fixed_matches.discard(word)
                            break
                        else:
                            wild_cards_local -= 1

                    elif wild_cards_local > 0:
                        wild_cards_local -= 1

                    else:
                        fixed_matches.discard(word)
                        break
            else:
                fixed_matches.discard(word)

    for word in fixed_matches:
        word_values[word.lower()] = sum([char_value[c] for c in word.lower()])

    for word in sorted(fixed_matches, key=lambda w: word_values[w.lower()]):
        print(word.lower() + ''.join('\t' * (ceil(len(max(fixed_matches, key=len)) / 4 + 0.1) - floor(len(word) / 4))) + str(word_values[word.lower()]))


def init():
    global words, letters
    words = choose_dict('english')
    letters = get_letters()
    scan_words()
    init()

init()
