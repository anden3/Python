def is_alphabetical(s):
    return s + (" IN" if list(s) == sorted(list(s)) else (" IN REVERSE" if list(s) == sorted(list(s), reverse=True) else " NOT IN")) + " ORDER"

print(is_alphabetical("sponged"))