vowels = ["a", "e", "i", "o", "u", "y", "å", "ä", "ö"]


def encode(s):
    result = ""
    for char in s:
        if char in vowels:
            result += char + "o" + char.lower()
        else:
            result += char
    return result


encode(input("Input: "))
