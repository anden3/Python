def return_alphabetized(word):
    word_list = list(word)

    indexes = []
    chars = []
    case = []

    for i, c in enumerate(word_list):
        if c.isalpha():
            indexes.append(i)
            chars.append(c.lower())
            case.append(c.isupper())

    chars = sorted(chars)

    for i, index in enumerate(indexes):
        if case[i]:
            word_list[index] = chars[i].upper()
        else:
            word_list[index] = chars[i]

    return ''.join(word_list)


def mangle_sentence(sentence):
    return ' '.join([return_alphabetized(word) for word in sentence.split()])

print(mangle_sentence("Eye of Newt, and Toe of Frog, Wool of Bat, and Tongue of Dog."))
print(mangle_sentence("Adder's fork, and Blind-worm's sting, Lizard's leg, and Howlet's wing."))
print(mangle_sentence("For a charm of powerful trouble, like a hell-broth boil and bubble."))