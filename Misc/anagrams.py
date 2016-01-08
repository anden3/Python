language = input("What language do you use?: ")

invalid_lines = []
valid_lines = []

if language[0:1] == 's':
    words = open('swedish_words.txt', 'r').read().split('\n')
else:
    words = open('/usr/share/dict/words', 'r').read().split('\n')

letters = list(input("What letters do you have?: ").lower())

letters_dict = {}

matches = []

for word in words:
    all_in_word = True

    for letter in letters:
        letters_dict[letter] = True

    if len(word) > 0:
        for char in word.lower():
            if not letters_dict.get(char, False) or char not in letters:
                all_in_word = False
                break
            elif letters_dict[char] and char in letters:
                letters_dict[char] = False

        if all_in_word:
            matches.append(word)

print(sorted(matches, key=len, reverse=True))
