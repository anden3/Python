from time import clock


def xor(value, key):
    return chr(ord(value) ^ ord(key))

t1 = clock()

file = open("cipher.txt")
encrypt = (file.read()).split(",")
file.close()

count = 0
pieces = {
    0: ""
}

for word in range(len(encrypt)):
    if word % 3 == 0 and word != 0:
        pieces[count] = pieces[count].strip(",")
        count += 1
        pieces[count] = ""
    pieces[count] += str(encrypt[word]) + ","

password = "god"

string = []
for piece in pieces:
    piece_array = str((pieces[piece])).split(",")

    if piece_array == ['73\n', '']:
        break

    string.append(xor(chr(int(piece_array[0])), password[0]))
    string.append(xor(chr(int(piece_array[1])), password[1]))
    string.append(xor(chr(int(piece_array[2])), password[2]))

print(''.join(string))
print(sum([ord(c) for c in string]))

t2 = clock()

print(str((t2 - t1) * 1000) + "ms")
