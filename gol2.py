import os
import time
import curses


class Cell:

    newlabel = ''

    def __init__(self, row, col, label):
        self.row = row
        self.col = col
        self.label = label

    def updatecell(self, celllist, boardsize):
        liveneighbours = self.getliveneighbours(celllist, boardsize)
        if liveneighbours < 2 or liveneighbours > 3:
            self.newlabel = ' '  # Makes cell dead
        elif liveneighbours == 2 and self.label == ' ':
            self.newlabel = ' '  # Keeps dead cell with 2 neighbours dead
        else:
            self.newlabel = 0  # Brings/keeps cell alive in other conditions

    def getliveneighbours(self, celllist, boardsize):
        count = 0
        for row in range(self.row-1, self.row+2):
            try:
                celllist[row]
            except KeyError:    # Handles vertical wrapping.
                if row < 0:
                    row += boardsize[0]
                else:
                    row -= boardsize[0]
            for col in range(self.col-1, self.col+2):
                try:
                    celllist[row][col]
                except IndexError:  # Handles horizontal wrapping.
                    if col < 0:
                        col += boardsize[1]
                    else:
                        col -= boardsize[1]
                if not celllist[row][col].label:
                    count += 1
        if not self.label:  # Subtracts the cell from the neighbours count
            return count-1
        else:
            return count

    def updatelabel(self):  # Updates the cell's label after all updates
        self.label = self.newlabel


class Board:
    celllist = {}  # Dict of rows

    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.generate()

    def printboard(self):  # Prints the board to the terminal using curses
        for num, row in self.celllist.items():
            line = ''
            for col, cell in enumerate(row):
                line += str(cell.label)
            terminal.addstr(num, 0, line)
        terminal.refresh()

    def generate(self):  # Adds all the cells to the board
        for row in range(self.rows-1):
            self.celllist[row] = []
            for col in range(self.columns):
                self.celllist[row].append(Cell(row, col, ' '))

    def updateboard(self):  # Updates each cell and then their label
        for row in self.celllist:
            for cell in self.celllist[row]:
                cell.updatecell(self.celllist, (self.rows-1, self.columns))
        for row in self.celllist:
            for cell in self.celllist[row]:
                cell.updatelabel()


if __name__ == "__main__":
    terminal = curses.initscr()  # Opens a curses window
    curses.noecho()
    curses.cbreak()
    terminal.nodelay(1)  # Don't wait for user input later
    rows, columns = os.popen('stty size', 'r').read().split()
    board = Board(int(rows), int(columns))
    board.celllist[6][8].label = 0  # Glider example starting position
    board.celllist[7][9].label = 0
    board.celllist[7][10].label = 0
    board.celllist[8][8].label = 0
    board.celllist[8][9].label = 0
    while 1:
        board.printboard()
        time.sleep(0.1)
        board.updateboard()
        char = terminal.getch()
        if char == 113:  # Checks for ASCII Char code for q to break loop
            break
    curses.endwin()  # Closes curses window
