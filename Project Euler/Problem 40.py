def prob():
    string = "0"
    arr = []
    for n in range(1, 200000):
        string += str(n)
    for x in string[::1]:
        arr.append(int(x))
    print(len(arr))
    return arr[1] * arr[10] * arr[100] * arr[1000] * arr[10000] * arr[100000] * arr[1000000]

print(prob())