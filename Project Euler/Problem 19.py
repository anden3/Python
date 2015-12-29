months = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31
}

sundays = 0
weekday = 0


def count_years():
    start = 1901
    end = 2000

    for n in range(start, end + 1):
        count_months(n)


def count_months(year):
    if year % 100 == 0:
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            months[2] = 29
        else:
            months[2] = 28
    for m in months:
        count_days(m)


def count_days(month):
    global sundays, weekday
    for d in range(month):
        if weekday == 6 and d == 0:
            sundays += 1
        elif weekday == 6:
            weekday = 0
        else:
            weekday += 1

count_years()
print(sundays)
