import random

letter_diff = {
    'a': (1 / 0.08167),
    'b': (1 / 0.01492),
    'c': (1 / 0.02782),
    'd': (1 / 0.04253),
    'e': (1 / 0.12702),
    'f': (1 / 0.02228),
    'g': (1 / 0.02015),
    'h': (1 / 0.06094),
    'i': (1 / 0.06966),
    'j': (1 / 0.00153),
    'k': (1 / 0.00772),
    'l': (1 / 0.04025),
    'm': (1 / 0.02406),
    'n': (1 / 0.06749),
    'o': (1 / 0.07507),
    'p': (1 / 0.01929),
    'q': (1 / 0.00095),
    'r': (1 / 0.05987),
    's': (1 / 0.06327),
    't': (1 / 0.09056),
    'u': (1 / 0.02758),
    'v': (1 / 0.00978),
    'w': (1 / 0.02361),
    'x': (1 / 0.00150),
    'y': (1 / 0.01974),
    'z': (1 / 0.00074)}
word_diff = {}


def generate_difficulty_list():
    for w in open('../Words/english_words.txt').read().split():
        unique_chars = set([c for c in w])
        word_diff[w] = sum([letter_diff[c] for c in unique_chars]) / len(w)


def draw_man(fails):
    man = {
        1: (2, 1, '0'),
        2: (3, 1, '|'),
        3: (3, 0, '/'),
        4: (3, 2, '\\'),
        5: (4, 0, '/'),
        6: (4, 2, '\\')
    }

    stage = [
        [' ', '+', '-', '-', '-', '+'],
        [' ', '|', ' ', ' ', ' ', '|'],
        [' ', ' ', ' ', ' ', ' ', '|'],
        [' ', ' ', ' ', ' ', ' ', '|'],
        [' ', ' ', ' ', ' ', ' ', '|'],
        [' ', ' ', ' ', ' ', ' ', '|'],
        ['=', '=', '=', '=', '=', '=']
    ]

    for i in range(1, fails + 1):
        stage[man[i][0]][man[i][1]] = man[i][2]

    for row in stage:
        print(''.join([cell for cell in row]))


def game():
    fail_limit = 6
    fails = 0

    word = random.choice(list(word_diff.keys())).lower()
    word_upper = word.upper()

    guessed_letters = []
    displayed_letters = [False for _ in range(len(word))]

    print("Difficulty: " + str(word_diff[word]))

    while True:
        draw_man(fails)

        print('\n' + ' '.join([l if displayed_letters[i] else '_' for i, l in enumerate(word_upper)]) +
              "\t\tGuessed letters: " + ' '.join(sorted([c.upper() for c in guessed_letters])))

        guess = input("What's your guess?: ").lower()

        if guess == word:
            print("You Win!")
            break

        elif len(guess) == 1 and guess in guessed_letters:
            print("You've already guessed that letter.")

        elif len(guess) == 1 and guess in word:
            guessed_letters.append(guess)
            print("Correct!")

            for i, l in enumerate(word):
                if guess == l:
                    displayed_letters[i] = True

        else:
            fails += 1
            guessed_letters.append(guess)
            print("Wrong!")

        if fails >= fail_limit:
            print("Game Over!\nThe word was " + word + '.')
            break


generate_difficulty_list()
game()
