def prob():
    n_list = []
    for a in range(2, 101):
        for b in range(2, 101):
            n_list.append(a ** b)
    return len(list(set(n_list)))

print(prob())