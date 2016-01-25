def get_weight(word, reverse=False):
    if reverse:
        return sum([(ord(c) - 64) * (len(word) - i) for i, c in enumerate(word)])
    else:
        return sum([(ord(c) - 64) * (i + 1) for i, c in enumerate(word)])


def get_balance_point(word):
    if not [print(word[:s] + ' ' + word[s:s + 1] + ' ' + word[s + 1:] + ' - ' + str(get_weight(word[:s], reverse=True))) for s in range(1, len(word)) if get_weight(word[:s], reverse=True) == get_weight(word[s + 1:])]:
        print(word + " DOES NOT BALANCE")

get_balance_point("STEAD")
