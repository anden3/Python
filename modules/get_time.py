from math import ceil
from time import perf_counter

spacing = 40
units = ['s', 'ms.', 'μs.', 'ns.']

function_times = {}

config = {
    "silent": False
}


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


def config_time(**kwargs):
    for key, value in kwargs.items():
        if key in config:
            config[key] = value


def time_function(f):
    def f_timer(*args, **kwargs):
        t1 = perf_counter()
        result = f(*args, **kwargs)
        t2 = perf_counter()

        t = abs(t2 - t1)

        if f.__name__ not in function_times:
            function_times[f.__name__] = [t]
        else:
            function_times[f.__name__].append(t)

        if not config["silent"]:
            print_converted(t, f.__name__)
        return result

    return f_timer


def get_function_avg(name=None):
    if len(function_times) > 0:
        print()

        if name is not None and name in function_times:
            print_converted(sum(function_times[name]) / len(function_times[name]), name + " Average")

        else:
            for function in function_times:
                print_converted(sum(function_times[function]) / len(function_times[function]), function + " Average")


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

    value = str(round(t, 3))

    if len(value) < 7:
        value += '0' * (7 - len(value))

    desc += ''.join(['\t'] * ceil((spacing - len(desc)) / 4))
    print(desc, value, unit)