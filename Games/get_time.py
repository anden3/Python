from math import ceil
from time import perf_counter

spacing = 40
units = ['s', 'ms.', 'μs.', 'ns.']


class Time:
    def __init__(self):
        self.timings = {}
        self.count = 0
        self.t0 = 0
        self.begun_last = False

    def add(self):
        t = perf_counter()

        if self.t0 != 0:
            self.count += 1
            self.timings[self.count] = t - self.t0
            self.t0 = 0

        else:
            self.t0 = t

    def get(self, get_type="last"):
        if len(self.timings) > 0:
            if get_type != "last":
                if not self.begun_last:
                    print()
                    self.begun_last = True

                if get_type == "average" or get_type == "avg":
                    print_converted(sum(self.timings.values()) / len(self.timings), "Average")
                elif get_type == "min":
                    print_converted(min(self.timings.values()), "Min")
                elif get_type == "max":
                    print_converted(max(self.timings.values()), "Max")

            elif get_type == "last":
                print_converted(self.timings[self.count], "Loop " + str(self.count))


def print_converted(t, text=None):
    unit = None

    if t >= 1000:
        t /= 60
        unit = "min."
    else:
        for u in units:
            if t >= 1:
                unit = u
                break
            else:
                t *= 1000

    assert unit is not None
    assert 1 <= t < 1000

    if text is not None:
        desc = "Time Taken (" + text + "):"
    else:
        desc = "Time Taken:"

    desc += ''.join(['\t'] * ceil((spacing - len(desc)) / 4))
    print(desc, round(t, 3), unit)