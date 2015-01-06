import sys
from math import sqrt
import curses


def prime(n1, n2, target):
    for x in range(n1, n2 + 1):
        p = True
        for y in range(2, int(sqrt(x) + 1)):
                if x % y == 0:
                    p = False
                    break
        if p:
            lst.append(str(x))
            if target is not None:
                if len(lst) == target:
                    return x
    return


def main(stdscr):
    global lst
    lst = []

    curses.curs_set(False)
    stdscr.clear()
    stdscr.border(0)

    stdscr.addstr(2, 25, "Extensible prime generator")
    stdscr.addstr(9, 5, "What would you like to do?")
    stdscr.addstr(10, 6, "1. Show the first X primes.")
    stdscr.addstr(11, 6, "2. Show primes between X and Y.")
    stdscr.addstr(12, 6, "3. Show the amount of primes between X and Y.")
    stdscr.addstr(13, 6, "4. Show the X:th prime.")
    stdscr.addstr(14, 6, "5. Quit.")
    stdscr.refresh()

    while True:
        c = stdscr.getkey()
        if c == "1":
            stdscr.clear()
            stdscr.border(0)
            stdscr.addstr(2, 25, "Extensible prime generator")
            stdscr.addstr(9, 5, "What value should X be?")
            stdscr.refresh()

            x = stdscr.getstr()

            if int(x) < 293:
                prime(2, int(x), None)
            else:
                stdscr.clear()
                stdscr.border(0)
                stdscr.addstr(2, 25, "Extensible prime generator")
                stdscr.addstr(9, 5, "Too much output")
                stdscr.refresh()

                stdscr.getch()
                curses.wrapper(main)

            stdscr.clear()
            stdscr.border(0)
            stdscr.addstr(2, 25, "Extensible prime generator")

            for n in lst:
                stdscr.addstr(9 + lst.index(n), 5, n + " ")

            stdscr.getch()
            curses.wrapper(main)

        elif c == "2":
            stdscr.clear()
            stdscr.border(0)
            stdscr.addstr(2, 25, "Extensible prime generator")
            stdscr.addstr(9, 5, "What value should X be?")
            stdscr.refresh()

            x = stdscr.getstr()

            stdscr.clear()
            stdscr.border(0)
            stdscr.addstr(2, 25, "Extensible prime generator")
            stdscr.addstr(9, 5, "What value should Y be?")
            stdscr.refresh()

            y = stdscr.getstr()

            prime(int(x), int(y), None)

            stdscr.clear()
            stdscr.border(0)
            stdscr.addstr(2, 25, "Extensible prime generator")

            for n in lst:
                stdscr.addstr(9 + lst.index(n), 5, n)

            stdscr.getch()
            curses.wrapper(main)

        elif c == "3":
            stdscr.clear()
            stdscr.border(0)
            stdscr.addstr(2, 25, "Extensible prime generator")
            stdscr.addstr(9, 5, "What value should X be?")
            stdscr.refresh()

            x = stdscr.getstr()

            stdscr.clear()
            stdscr.border(0)
            stdscr.addstr(2, 25, "Extensible prime generator")
            stdscr.addstr(9, 5, "What value should Y be?")
            stdscr.refresh()

            y = stdscr.getstr()

            prime(int(x), int(y), None)

            stdscr.clear()
            stdscr.border(0)
            stdscr.addstr(2, 25, "Extensible prime generator")

            stdscr.addstr(9, 5, str(len(lst)))

            stdscr.getch()
            curses.wrapper(main)

        elif c == "4":
            stdscr.clear()
            stdscr.border(0)
            stdscr.addstr(2, 25, "Extensible prime generator")
            stdscr.addstr(9, 5, "What value should X be?")
            stdscr.refresh()

            tar = stdscr.getstr()

            stdscr.clear()
            stdscr.border(0)
            stdscr.addstr(2, 25, "Extensible prime generator")

            stdscr.addstr(9, 5, str(prime(2, 1000000, int(tar))))

            stdscr.getch()
            curses.wrapper(main)

        elif c == "5":
            sys.exit()

curses.wrapper(main)