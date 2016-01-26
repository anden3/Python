vowels = ["a", "e", "i", "o", "u", "y", "å", "ä", "ö"]


def encode_word(w):
    result = ""

    for c in w:
        if c.lower() not in vowels and c.isalpha():
            if c.isupper():
                result += c + "o" + c.lower()
            else:
                result += c + "o" + c
        else:
            result += c

    return result


def decode_word(w):
    chars = list(w)

    for i, c in enumerate(chars):
        if c.lower() not in vowels and c.isalpha():
            chars.pop(i + 1)
            chars.pop(i + 1)

    return ''.join(chars)


def encode(s):
    return ' '.join([encode_word(w) for w in s.split()])


def decode(s):
    return ' '.join([decode_word(w) for w in s.split()])


print(encode("I'm speaking Robber's language!"))
print(decode(encode("I'm speaking Robber's language!")))
