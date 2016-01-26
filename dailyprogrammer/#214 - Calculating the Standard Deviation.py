from time import perf_counter


def standard_deviation(values):
    return (sum([(value - (sum(values) / len(values))) ** 2 for value in values]) / len(values)) ** 0.5

t1 = perf_counter()

print(standard_deviation([266, 344, 375, 399, 409, 433, 436, 440, 449, 476, 502, 504, 530, 584, 587]))
print(standard_deviation([809, 816, 833, 849, 851, 961, 976, 1009, 1069, 1125, 1161, 1172, 1178, 1187, 1208, 1215, 1229, 1241, 1260, 1373]))

print(str((perf_counter() - t1) * 1000) + " ms.")
