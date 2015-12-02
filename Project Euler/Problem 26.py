def get_decimal(n):
    val = 1 / n
    val_str = str(val)[2::]
    arr = []
    repeating = []

    for c in val_str[0::]:
        if c in arr:
            c_arr_pos = arr.index(c)
            c_str_pos = val_str.index(c)

            if arr[c_arr_pos + 1] == val_str[c_str_pos + 1] and arr[c_arr_pos + 2] == val_str[c_str_pos + 2]:
                return repeating
            else:
                repeating.append(c)
        else:
            repeating.append(c)

        arr.append(c)

get_decimal(3)
