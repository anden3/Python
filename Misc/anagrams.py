from math import floor

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
    'r': 1,
    's': 1,
    't': 1,
    'u': 4,
    'v': 3,
    'x': 8,
    'y': 7,
    'z': 8,
    'å': 4,
    'ä': 4,
    'ö': 4
}


def choose_dict():
    language = input("Swedish or English?: ")

    if language[0:1].lower() == 's':
        return open('swedish_words.txt', 'r').read().split('\n')
    elif language[0:1].lower() == 'e':
        return open('/usr/share/dict/words', 'r').read().split('\n')
    else:
        print("Unknown language, please try again.")
        return choose_dict()


def get_letters():
    chars = list(input("What letters do you have?: ").replace(' ', '').replace('w', '').lower())
    copy = chars.copy()

    for i, c in enumerate(copy):
        if c.isdigit():
            if i < len(copy) - 1 and not copy[i + 1].isdigit():
                fixed_letters[int(c) - 1] = copy[i + 1]
                chars.remove(c)

    return chars


def scan_words():
    fixed_matches = set(words)
    word_values = {}

    if len(fixed_letters) > 0:
        for char_index in fixed_letters:
            for word in fixed_matches.copy():
                if len(word) - 1 >= max(fixed_letters):
                    if word[char_index].lower() != fixed_letters[char_index]:
                        fixed_matches.discard(word)
                else:
                    fixed_matches.discard(word)

    for word in fixed_matches.copy():
        for letter in letters:
            letters_dict[letter] = True

        if len(word) > 0:
            for char in word.lower():
                if not letters_dict.get(char, False) or char not in letters:
                    fixed_matches.discard(word)
                    break
                else:
                    letters_dict[char] = False
        else:
            fixed_matches.discard(word)

    for word in fixed_matches:
        word_values[word.lower()] = sum([char_value[c] for c in word.lower()])

    for word in sorted(fixed_matches, key=lambda w: word_values[w.lower()]):
        print(word.lower() + ''.join('\t' * (3 - floor(len(word) / 4))) + str(word_values[word.lower()]))


def init():
    global words, letters
    words = choose_dict()
    letters = get_letters()
    scan_words()

init()
