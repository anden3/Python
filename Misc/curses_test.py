import sys
import curses
from math import floor

sys.setrecursionlimit(1000000)

board = []

m_x = [0]
m_y = [0]
space = [0]


def make_board(size):
    for x in range(size):
        board.append(["_"] * size)


def main(stdscr):
    curses.curs_set(False)
    stdscr.clear()
    stdscr.border(0)
    dim = stdscr.getmaxyx()

    stdscr.addstr(2, floor(dim[1] / 2 - 4), "Game test")

    for n in range(len(board)):
        stdscr.addstr(5 + n, floor(dim[1] / 2 - len(board)), " ".join(board[n]))

    if space[0] == 1:
        board[m_x[0]][m_y[0]] = "#"
        space[0] = 0
    else:
        board[m_x[0]][m_y[0]] = "_"

    c = stdscr.getch()

    if c == curses.KEY_UP and m_x[0] != 0:
        m_x[0] -= 1
    elif c == curses.KEY_DOWN and m_x[0] != len(board) - 1:
        m_x[0] += 1
    elif c == curses.KEY_LEFT and m_y[0] != 0:
        m_y[0] -= 1
    elif c == curses.KEY_RIGHT and m_y[0] != len(board) - 1:
        m_y[0] += 1
    elif c == ord(' '):
        space[0] = 1
    elif c == ord('q'):
        sys.exit()

    board[m_x[0]][m_y[0]] = "X"

    stdscr.refresh()

    curses.wrapper(main)

make_board(66)

curses.wrapper(main)