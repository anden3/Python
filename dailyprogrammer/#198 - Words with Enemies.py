def word_diff(a, b):
    for c in a + b:
        if c in a and c in b:
            a.remove(c)
            b.remove(c)

    return "A: " + ''.join(a) + "\nB: " + ''.join(b) + '\n' + ("Tie!" if len(a) == len(b) else ("Left Wins!" if len(a) > len(b) else "Right Wins!"))

print(word_diff(list("hello"), list("below")))
