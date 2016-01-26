from time import perf_counter


def generate_function(args, n, cycles):
    print("Term 0: " + str(n))

    base = (len(args.split()) * '(') + 'x'

    for arg in args.split():
        base += ' ' + ' '.join(list(arg)) + ')'

    for c in range(1, cycles + 1):
        n = eval(base, {'x': n})
        print("Term " + str(c) + ": " + str(n))

t1 = perf_counter()
generate_function("+2 *3 -5", 0, 10)
print(str((perf_counter() - t1) * 1000) + " ms.")
