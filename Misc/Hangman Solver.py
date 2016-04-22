import re


def hangman():
    file = open("../Words/english_words.txt")
    words = file.readlines()
    file.close()

    letters = {}
    rejected_letters = set()
    length = int(input("What's the length of the word?: "))

    matches = set()

    while True:
        new_letter = input("What's the new letter?: ")
        rejected = input("Was it wrong?: ")

        if rejected == "yes":
            rejected_letters.add(new_letter)
        else:
            new_position = int(input("What's its position?: "))
            letters[new_position] = new_letter

        regex_string = "^"
        set_length = 0

        for i in range(1, length + 1):
            if letters.get(i) is not None:
                if set_length > 0:
                    regex_string += "{" + str(set_length) + "}"
                    set_length = 0

                regex_string += letters[i]

            else:
                if len(rejected_letters) > 0:
                    if set_length == 0:
                        regex_string += "[^" + "".join(rejected_letters) + "]"
                        set_length += 1
                    else:
                        set_length += 1
                else:
                    regex_string += "."

        if set_length > 0:
            regex_string += "{" + str(set_length) + "}"

        regex = re.compile(regex_string + "$", re.IGNORECASE)

        if len(matches) != 0:
            for match in matches.copy():
                m = regex.match(match)

                if m is None:
                    matches.discard(match)
                else:
                    print(match)

            if len(matches) == 0:
                print("No matches found.")
                return

        else:
            for word in words:
                m = regex.match(word)

                if m is not None:
                    matches.add(word)
                    print(word)

hangman()