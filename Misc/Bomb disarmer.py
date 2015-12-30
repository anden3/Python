from itertools import groupby
from re import finditer

from math import ceil

positions = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth",
    6: "sixth"
}

color_names = {
    'r': 'red',
    'b': 'blue',
    'g': 'green',
    'y': 'yellow',
    'w': 'white',
    's': 'black'
}

vowels = ['a', 'e', 'i', 'o', 'u']

batteries = None
serial_number = None
last_digit_odd = None
has_parallel = None


def get_occurrences(c, s):
    return len([char for char in finditer(c, s)])


def get_last_pos(c, s):
    return positions[''.join(s).rfind(c) + 1]


def get_batteries():
    global batteries

    if batteries is None:
        batteries = int(input("How many batteries are on the bomb?: "))

    return batteries


def get_indicator(label):
    return input("Is there a lit indicator with the label " + label.upper() + " on the bomb?: ")[0:1] == "y"


def get_parallel():
    global has_parallel

    if has_parallel is None:
        has_parallel = input("Is there a parallel port on the bomb?: ").lower()[0:1] == "y"

    return has_parallel


def get_serial(last_digit):
    global serial_number

    if serial_number is None:
        serial_number = input("What is the serial number?: ").lower()

    if last_digit:
        if last_digit_odd is None:
            for n in serial_number[::-1]:
                if n.isnumeric():
                    return int(n) % 2 == 1
        else:
            return last_digit_odd
    else:
        return serial_number


def simple_wires():
    wires = input("Which wires do you have?: ")
    wire_amount = len(wires)

    if 3 <= wire_amount <= 6:
        if wire_amount == 3:
            if 'r' not in wires:
                print("Cut the second wire.")

            elif wires.endswith('w'):
                print("Cut the last wire.")

            elif get_occurrences('b', wires) > 1:
                print("Cut the " + get_last_pos('b', wires) + " wire.")

            else:
                print("Cut the last wire.")

        elif wire_amount == 4:
            if get_occurrences('r', wires) > 1 and get_serial(True):
                print("Cut the " + get_last_pos('r', wires) + " wire.")

            elif wires.endswith('y') and 'r' not in wires:
                print("Cut the first wire.")

            elif get_occurrences('b', wires) == 1:
                print("Cut the first wire.")

            elif get_occurrences('y', wires) > 1:
                print("Cut the last wire.")

            else:
                print("Cut the second wire.")

        elif wire_amount == 5:
            if wires.endswith('s') and get_serial(True):
                print("Cut the fourth wire.")

            elif get_occurrences('r', wires) == 1 and get_occurrences('y', wires) > 1:
                print("Cut the first wire.")

            elif 's' not in wires:
                print("Cut the second wire.")

            else:
                print("Cut the first wire.")

        elif wire_amount == 6:
            if 'y' not in wires and get_serial(True):
                print("Cut the third wire.")

            elif get_occurrences('y', wires) == 1 and get_occurrences('w', wires) > 1:
                print("Cut the fourth wire.")

            elif 'r' not in wires:
                print("Cut the last wire.")

            else:
                print("Cut the fourth wire.")
        module()


def button():
    color = input("What's the color of the button?: ").lower()[0:1]
    label = input("What's the label on the button?: ").lower()

    if color == "b" and label == "abort":
        button_strip()

    elif label == "detonate" and get_batteries() > 1:
        print("Hold and immediately release the button.")
        module()

    elif color == "w" and get_indicator("car"):
        button_strip()

    elif get_batteries() > 2 and get_indicator("frk"):
        print("Hold and immediately release the button.")
        module()

    elif color == "y":
        button_strip()

    elif color == "r" and label == "hold":
        print("Hold and immediately release the button.")
        module()

    else:
        button_strip()


def button_strip():
    print("Hold the button down. Check the color of the strip to the right of the button.")
    print("If the strip is blue, release when there's a 4 in the countdown timer.")
    print("If the strip is yellow, release when there's a 5 in the countdown timer.")
    print("If the strip is any other color, release when there's a 1 in the countdown timer.")

    module()


def simon_says():
    colors = ""

    if any(vowel in get_serial(False) for vowel in vowels):
        replace_chars = {
            'r': 'b',
            'b': 'r',
            'g': 'y',
            'y': 'g'
        }
    else:
        replace_chars = {
            'r': 'b',
            'b': 'y',
            'g': 'g',
            'y': 'r'
        }

    while True:
        if colors != "":
            colors += " + "

        colors += color_names[replace_chars[input("What new color is flashing?: ")]].capitalize()

        print("Press " + colors + ".")

        if input("Is the module disarmed?: ").lower()[0:1] == "y":
            module()


def correct_word():
    label_location = {
        "yes": "middle-left",
        "first": "top-right",
        "display": "bottom-right",
        "okay": "top-right",
        "says": "bottom-right",
        "nothing": "middle-left",
        "": "bottom-left",
        "blank": "middle-right",
        "no": "bottom-right",
        "led": "middle-left",
        "lead": "bottom-right",
        "read": "middle-right",
        "red": "middle-right",
        "reed": "bottom-left",
        "leed": "bottom-left",
        "hold on": "bottom-right",
        "you": "middle-right",
        "you are": "bottom-right",
        "your": "middle-right",
        "you're": "middle-right",
        "ur": "top-left",
        "there": "bottom-right",
        "they're": "bottom-left",
        "their": "middle-right",
        "they are": "middle-left",
        "see": "bottom-right",
        "c": "top-right",
        "cee": "bottom-right"
    }

    label_list = {
        "ready": ["yes", "okay", "what", "middle", "left", "press", "right", "blank", "ready", "no", "first", "uhhh", "nothing", "wait"],
        "first": ["left", "okay", "yes", "middle", "no", "right", "nothing", "uhhh", "wait", "ready", "blank", "what", "press", "first"],
        "no": ["blank", "uhhh", "wait", "first", "what", "ready", "right", "yes", "nothing", "left", "press", "okay", "no", "middle"],
        "blank": ["wait", "right", "okay", "middle", "blank", "press", "ready", "nothing", "no", "what", "left", "uhhh", "yes", "first"],
        "nothing": ["uhhh", "right", "okay", "middle", "yes", "blank", "no", "press", "left", "what", "wait", "first", "nothing", "ready"],
        "yes": ["okay", "right", "uhhh", "middle", "first", "what", "press", "ready", "nothing", "yes", "left", "blank", "no", "wait"],
        "what": ["uhhh", "what", "left", "nothing", "ready", "blank", "middle", "no", "okay", "first", "wait", "yes", "press", "right"],
        "uhhh": ["ready", "nothing", "left", "what", "okay", "yes", "right", "no", "press", "blank", "uhhh", "middle", "wait", "first"],
        "left": ["right", "left", "first", "no", "middle", "yes", "blank", "what", "uhhh", "wait", "press", "ready", "okay", "nothing"],
        "right": ["yes", "nothing", "ready", "press", "no", "wait", "what", "right", "middle", "left", "uhhh", "blank", "okay", "first"],
        "middle": ["blank", "ready", "okay", "what", "nothing", "press", "no", "wait", "left", "middle", "right", "first", "uhhh", "yes"],
        "okay": ["middle", "no", "first", "yes", "uhhh", "nothing", "wait", "okay", "left", "ready", "blank", "press", "what", "right"],
        "wait": ["uhhh", "no", "blank", "okay", "yes", "left", "first", "press", "what", "wait", "nothing", "ready", "right", "middle"],
        "press": ["right", "middle", "yes", "ready", "press", "okay", "nothing", "uhhh", "blank", "left", "first", "what", "no", "wait"],
        "you": ["sure", "you are", "your", "you're", "next", "uh huh", "ur", "hold", "what?", "you", "uh uh", "like", "done", "u"],
        "you are": ["your", "next", "like", "uh huh", "what?", "done", "uh uh", "hold", "you", "u", "you're", "sure", "ur", "you are"],
        "your": ["uh uh", "you are", "uh huh", "your", "next", "ur", "sure", "u", "you're", "you", "what?", "hold", "like", "done"],
        "you're": ["you", "you're", "ur", "next", "uh uh", "you are", "u", "your", "what?", "uh huh", "sure", "done", "like", "hold"],
        "ur": ["done", "u", "ur", "uh huh", "what?", "sure", "your", "hold", "you're", "like", "next", "uh uh", "you are", "you"],
        "u": ["uh huh", "sure", "next", "what?", "you're", "ur", "uh uh", "done", "u", "you", "like", "hold", "you are", "your"],
        "uh huh": ["uh huh", "your", "you are", "you", "done", "hold", "uh uh", "next", "sure", "like", "you're", "ur", "u", "what?"],
        "uh uh": ["ur", "u", "you are", "you're", "next", "uh uh", "done", "you", "uh huh", "like", "your", "sure", "hold", "what?"],
        "what?": ["you", "hold", "you're", "your", "u", "done", "uh uh", "like", "you are", "uh huh", "ur", "next", "what?", "sure"],
        "done": ["sure", "uh huh", "next", "what?", "your", "ur", "you're", "hold", "like", "you", "u", "you are", "uh uh", "done"],
        "next": ["what?", "uh huh", "uh uh", "your", "hold", "sure", "next", "like", "done", "you are", "ur", "you're", "u", "you"],
        "hold": ["you are", "u", "done", "uh uh", "you", "ur", "sure", "what?", "you're", "next", "hold", "uh huh", "your", "like"],
        "sure": ["you are", "done", "like", "you're", "you", "hold", "uh huh", "ur", "sure", "u", "what?", "next", "your", "uh uh"],
        "like": ["you're", "next", "u", "ur", "hold", "done", "uh uh", "what?", "uh huh", "you", "like", "sure", "you are", "your"]
    }

    for x in range(3):
        displayed_word = input("What's the word on the display?: ").lower()
        search_word = input("What word is in the " + label_location[displayed_word] + "?: ")

        for word in label_list[search_word]:
            if input("Is the word " + word + " in the list?: ").lower()[0:1] == "y":
                print("Click it.")
                break

    module()


def memory():
    first_value = int(input("What's the number in the big display?: "))
    s1_vals = []

    if first_value == 1:
        s1_vals.append(int(input("What number is at the second position?: ")))
        s1_vals.append(2)

        print("Click " + str(s1_vals[0]) + " at the " + positions[s1_vals[1]] + " position.")
    else:
        s1_vals.append(int(input("What number is at the " + positions[first_value] + " position?: ")))
        s1_vals.append(first_value)

        print("Click " + str(s1_vals[0]) + " at the " + positions[s1_vals[1]] + " position.")

    second_value = int(input("What's the number in the big display?: "))
    s2_vals = []

    if second_value == 1:
        s2_vals.append(4)
        s2_vals.append(int(input("What position does the number 4 have?: ")))

        print("Click " + str(s2_vals[0]) + " at the " + positions[s2_vals[1]] + " position.")

    elif second_value == 2 or second_value == 4:
        s2_vals.append(int(input("What number is at the " + positions[s1_vals[1]] + " position?: ")))
        s2_vals.append(s1_vals[1])

        print("Click " + str(s2_vals[0]) + " at the " + positions[s2_vals[1]] + " position.")

    else:
        s2_vals.append(int(input("What number is at the first position?: ")))
        s2_vals.append(1)

        print("Click " + str(s2_vals[0]) + " at the " + positions[s2_vals[1]] + " position.")

    third_value = int(input("What's the number in the big display?: "))
    s3_vals = []

    if third_value == 1:
        s3_vals.append(s2_vals[0])
        s3_vals.append(int(input("What position does the number " + str(s2_vals[0]) + " have?: ")))

        print("Click " + str(s3_vals[0]) + " at the " + positions[s3_vals[1]] + " position.")

    elif third_value == 2:
        s3_vals.append(s1_vals[0])
        s3_vals.append(int(input("What position does the number " + str(s1_vals[0]) + " have?: ")))

        print("Click " + str(s3_vals[0]) + " at the " + positions[s3_vals[1]] + " position.")

    elif third_value == 3:
        s3_vals.append(int(input("What number is at the third position?: ")))
        s3_vals.append(third_value)

        print("Click " + str(s3_vals[0]) + " at the " + positions[s3_vals[1]] + " position.")

    else:
        s3_vals.append(4)
        s3_vals.append(int(input("What position does the number 4 have?: ")))

        print("Click " + str(s3_vals[0]) + " at the " + positions[s3_vals[1]] + " position.")

    fourth_value = int(input("What's the number in the big display?: "))
    s4_vals = []

    if fourth_value == 1:
        s4_vals.append(int(input("What number is at the " + positions[s1_vals[1]] + " position?: ")))
        s4_vals.append(s1_vals[1])

        print("Click " + str(s4_vals[0]) + " at the " + positions[s4_vals[1]] + " position.")

    elif fourth_value == 2:
        s4_vals.append(int(input("What number is at the first position?: ")))
        s4_vals.append(1)

        print("Click " + str(s4_vals[0]) + " at the " + positions[s4_vals[1]] + " position.")

    else:
        s4_vals.append(int(input("What number is at the " + positions[s2_vals[1]] + " position?: ")))
        s4_vals.append(s2_vals[1])

        print("Click " + str(s4_vals[0]) + " at the " + positions[s4_vals[1]] + " position.")

    fifth_value = int(input("What's the number in the big display?: "))

    if fifth_value == 1:
        print("Press the button labeled " + str(s1_vals[0]) + ".")
    elif fifth_value == 2:
        print("Press the button labeled " + str(s2_vals[0]) + ".")
    elif fifth_value == 3:
        print("Press the button labeled " + str(s4_vals[0]) + ".")
    else:
        print("Press the button labeled " + str(s3_vals[0]) + ".")

    module()


def morse_code():
    words = {
        "shell": 3.505,
        "halls": 3.515,
        "slick": 3.522,
        "trick": 3.532,
        "boxes": 3.535,
        "leaks": 3.542,
        "strobe": 3.545,
        "bistro": 3.552,
        "flick": 3.555,
        "bombs": 3.565,
        "break": 3.572,
        "brick": 3.575,
        "steak": 3.582,
        "sting": 3.592,
        "vector": 3.595,
        "beats": 3.600
    }

    translation_table = {
        '.-': 'a',
        '-...': 'b',
        '-.-.': 'c',
        '.': 'e',
        '..-.': 'f',
        '--.': 'g',
        '....': 'h',
        '..': 'i',
        '-.-': 'k',
        '.-..': 'l',
        '--': 'm',
        '-.': 'n',
        '---': 'o',
        '.-.': 'r',
        '...': 's',
        '-': 't',
        '...-': 'v',
        '-..-': 'x'
    }

    code_word = [translation_table[char] for char in input("Type the short flashes as dots, long flashes as dashes, and pauses as spaces: ").split()]
    matches = []

    for word in words:
        is_match = True

        for letter in code_word:
            if letter not in word:
                is_match = False

        if is_match:
            matches.append(word)

    if len(matches) > 1:
        print("Too many matches, please try again.")
        morse_code()
    else:
        print("Set the frequency to " + str(words[matches[0]]) + " MHz.")
        module()


def complicated_wires():
    wire_count = int(input("How many wires are there?: "))

    for wire in range(wire_count):
        wire_red = input("Is the wire red?: ").lower()[0:1] == "y"
        wire_blue = input("Is the wire blue?: ").lower()[0:1] == "y"

        wire_symbol = input("Is there a star symbol underneath the wire?: ").lower()[0:1] == "y"
        wire_led = input("Is the LED above the wire lit?: ").lower()[0:1] == "y"

        if wire_red:
            if wire_blue:
                if wire_symbol:
                    if wire_led:
                        print("Do not cut the wire.")
                    else:
                        if get_parallel():
                            print("Cut the wire.")
                        else:
                            print("Do not cut the wire.")
                else:
                    if not get_serial(True):
                        print("Cut the wire.")
                    else:
                        print("Do not cut the wire.")
            else:
                if wire_symbol:
                    if wire_led:
                        if get_batteries() >= 2:
                            print("Cut the wire.")
                        else:
                            print("Do not cut the wire.")
                    else:
                        print("Cut the wire.")
                else:
                    if wire_led:
                        if get_batteries() >= 2:
                            print("Cut the wire.")
                        else:
                            print("Do not cut the wire.")
                    else:
                        if not get_serial(True):
                            print("Cut the wire.")
                        else:
                            print("Do not cut the wire.")
        else:
            if wire_blue:
                if wire_symbol:
                    if wire_led:
                        if get_parallel():
                            print("Cut the wire.")
                        else:
                            print("Do not cut the wire.")
                    else:
                        print("Do not cut the wire.")
                else:
                    if wire_led:
                        if get_parallel():
                            print("Cut the wire.")
                        else:
                            print("Do not cut the wire.")
                    else:
                        if not get_serial(True):
                            print("Cut the wire.")
                        else:
                            print("Do not cut the wire.")
            else:
                if wire_symbol:
                    if wire_led:
                        if get_batteries() >= 2:
                            print("Cut the wire.")
                        else:
                            print("Do not cut the wire.")
                    else:
                        print("Cut the wire.")
                else:
                    if wire_led:
                        print("Do not cut the wire.")
                    else:
                        print("Cut the wire.")

    module()


def wire_sequences():
    red_occurences = ["c", "b", "a", "ac", "b", "ac", "abc", "ab", "b"]
    blue_occurences = ["b", "ac", "b", "a", "b", "bc", "c", "ac", "a"]
    black_occurences = ["abc", "ac", "b", "ac", "b", "bc", "ab", "c", "c"]

    red_wires = 0
    blue_wires = 0
    black_wires = 0

    for x in range(100):
        if x == 0:
            wire_color = input("What's the color of the first wire on the left?: ").lower()
        else:
            wire_color = input("What's the color of the next wire?: ").lower()

        if wire_color == "x":
            return

        wire_target = input("Where does the wire lead to?: ").lower()

        if wire_color == "red" or wire_color == "r":
            if wire_target in red_occurences[red_wires]:
                print("Cut the wire.")
            else:
                print("Do not cut the wire.")

            red_wires += 1

        elif wire_color == "blue" or wire_color == "b":
            if wire_target in blue_occurences[blue_wires]:
                print("Cut the wire.")
            else:
                print("Do not cut the wire.")

            blue_wires += 1

        elif wire_color == "black" or wire_color == "s":
            if wire_target in black_occurences[black_wires]:
                print("Cut the wire.")
            else:
                print("Do not cut the wire.")

            black_wires += 1


def maze():
    maze_1 = [
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    ]

    maze_2 = [
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        [0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0],
        [0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0]
    ]

    maze_3 = [
        [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
        [0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0],
        [1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        [0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0],
        [0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
    ]

    maze_4 = [
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0]
    ]

    maze_5 = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    maze_6 = [
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0],
        [0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0],
        [1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
    ]

    maze_7 = [
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    maze_8 = [
        [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
        [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    maze_9 = [
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0],
        [0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    ]

    mazes = {
        '21': maze_1,
        '36': maze_1,

        '25': maze_2,
        '42': maze_2,

        '44': maze_3,
        '46': maze_3,

        '11': maze_4,
        '41': maze_4,

        '35': maze_5,
        '64': maze_5,

        '15': maze_6,
        '53': maze_6,

        '12': maze_7,
        '62': maze_7,

        '14': maze_8,
        '43': maze_8,

        '23': maze_9,
        '51': maze_9
    }

    mark = ''.join(input("What's the row and column of one of the green circles?: ").split())
    if mark not in mazes:
        print("Invalid position, please try again")
        maze()

    active_maze = mazes[mark]

    player_pos = [int(c) for c in input("What's the row and column of the white square?: ").split()]

    while player_pos[0] < 1 or player_pos[0] > 6 or player_pos[1] < 1 or player_pos[1] > 6:
        print("Invalid position given, please try again.")
        player_pos = [int(c) for c in input("What's the row and column of the white square?: ").split()]

    target_pos = [int(c) for c in input("What's the row and column of the red triangle?: ").split()]

    while target_pos[0] < 1 or target_pos[0] > 6 or target_pos[1] < 1 or target_pos[1] > 6:
        print("Invalid position given, please try again.")
        target_pos = [int(c) for c in input("What's the row and column of the red triangle?: ").split()]

    active_maze[target_pos[0] * 2 - 2][target_pos[1] * 2 - 2] = 2

    def search(x, y):
        if active_maze[x][y] == 2:
            return True

        elif active_maze[x][y] == 1 or active_maze[x][y] == 3:
            return False

        active_maze[x][y] = 3

        if (x < len(active_maze[0]) - 1 and search(x + 1, y)) or (y > 0 and search(x, y - 1)) or (x > 0 and search(x - 1, y)) or (y < len(active_maze) - 1 and search(x, y + 1)):
            return True

        active_maze[x][y] = 0
        return False

    search(player_pos[0] * 2 - 2, player_pos[1] * 2 - 2)

    steps = []

    def find_steps(x, y, prev_rel_loc):
        if x > 0 and prev_rel_loc != "up" and active_maze[x - 1][y] == 3:
            steps.append("Up")
            find_steps(x - 1, y, "down")
        elif y < len(active_maze[x]) - 1 and prev_rel_loc != "right" and active_maze[x][y + 1] == 3:
            steps.append("Right")
            find_steps(x, y + 1, "left")
        elif x < len(active_maze) - 1 and prev_rel_loc != "down" and active_maze[x + 1][y] == 3:
            steps.append("Down")
            find_steps(x + 1, y, "up")
        elif y > 0 and prev_rel_loc != "left" and active_maze[x][y - 1] == 3:
            steps.append("Left")
            find_steps(x, y - 1, "right")
        else:
            parse_steps(steps)

    def parse_steps(arr):
        grouped_list = [list(j) for i, j in groupby(arr)]

        for group in grouped_list:
            print(group[0] + ": " + str(ceil(len(group) / 2)))

        module()

    find_steps(player_pos[0] * 2 - 2, player_pos[1] * 2 - 2, "")


def password():
    passwords = ["about", "after", "again", "below", "could", "every", "first", "found", "great", "house",
                 "large", "learn", "never", "other", "place", "plant", "point", "right", "small", "sound",
                 "spell", "still", "study", "their", "there", "these", "thing", "think", "three", "water",
                 "where", "which", "world", "would", "write"]

    first_letter = list(input("What letters can the first letter be?: "))
    poss_pass_1 = []

    for letter in first_letter:
        poss_pass_1 += [pw for pw in passwords if letter == pw[0:1]]

    if len(poss_pass_1) > 1:
        second_letter = list(input("What letters can the second letter be?: "))
        poss_pass_2 = []

        for letter in second_letter:
            poss_pass_2 += [pw for pw in poss_pass_1 if letter == pw[1:2]]

        if len(poss_pass_2) > 1:
            third_letter = list(input("What letters can the third letter be?: "))
            poss_pass_3 = []

            for letter in third_letter:
                poss_pass_3 += [pw for pw in poss_pass_2 if letter == pw[2:3]]

            if len(poss_pass_3) > 1:
                fourth_letter = list(input("What letters can the fourth letter be?: "))
                poss_pass_4 = []

                for letter in fourth_letter:
                    poss_pass_4 += [pw for pw in poss_pass_3 if letter == pw[3:4]]

                if len(poss_pass_4) > 1:
                    fifth_letter = list(input("What letters can the fifth letter be?: "))
                    poss_pass_5 = []

                    for letter in fifth_letter:
                        poss_pass_5 += [pw for pw in poss_pass_4 if letter == pw[4:5]]

                    print(poss_pass_5[0])
                else:
                    print(poss_pass_4[0])
            else:
                print(poss_pass_3[0])
        else:
            print(poss_pass_2[0])
    else:
        print(poss_pass_1[0])

    module()

modules = {
    'wires': simple_wires,
    'button': button,
    'simon says': simon_says,
    'word': correct_word,
    'memory': memory,
    'morse': morse_code,
    'comp wires': complicated_wires,
    'wire seq': wire_sequences,
    'maze': maze,
    'password': password
}


def module():
    command = input("What module do you need help with?: ").lower()

    if command == "exit":
        return
    elif command not in modules:
        print("Invalid command, please try again.")
        module()
    else:
        return modules[command.lower()]()

print(module())
