import os
import time
import curses
import random


class Cell:

    newlabel = ''

    def __init__(self, row, col, label):
        self.row = row
        self.col = col
        self.label = label

    def updatecell(self, celllist, boardsize):
        liveneighbours = self.getliveneighbours(celllist, boardsize)
        if liveneighbours < 2 or liveneighbours > 3:
            self.newlabel = True  # Makes cell dead
        elif liveneighbours == 2 and self.label:
            self.newlabel = True  # Keeps dead cell with 2 neighbours dead
        else:
            self.newlabel = False  # Keeps cell alive in other conditions

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

    def __init__(self, rows, columns, random):
        self.rows = rows
        self.columns = columns
        self.random = random
        self.generate()

    def printboard(self):  # Prints the board to the terminal using curses
        for num, row in self.celllist.items():
            line = ''
            for col, cell in enumerate(row):
                if cell.label:
                    line += ' '
                else:
                    line += '0'
            terminal.addstr(num, 0, line)
        terminal.refresh()

    def generate(self):  # Adds all the cells to the board
        for row in range(self.rows-1):
            self.celllist[row] = []
            for col in range(self.columns):
                if self.random:
                    self.celllist[row].append(Cell(row, col,
                                                   bool(random.getrandbits(1)
                                                        )))
                else:
                    self.celllist[row].append(Cell(row, col, True))

    def updateboard(self):  # Updates each cell and then their label
        for row in self.celllist:
            for cell in self.celllist[row]:
                cell.updatecell(self.celllist, (self.rows-1, self.columns))
        for row in self.celllist:
            for cell in self.celllist[row]:
                cell.updatelabel()


def getfiles():  # Loads all the pattern files
    files = []
    print('State files (stored in examples directory):')
    for file in os.listdir("examples"):
        if file.endswith(".txt"):
            files.append(os.path.join("examples/", file))
    return files


def randomboard(rows, columns):  # Sets the cell values to random
    board = Board(int(rows), int(columns), True)
    return board


def loadboard(rows, columns):  # Handles choosing a file and loading it
    board = Board(int(rows), int(columns), False)
    files = getfiles()
    for num, file in enumerate(files):
        print(str(num) + ': ' + file)
    validfile = False
    file = ''
    a = input('Type the number of the selected file to load it: ')
    while not validfile:
        try:
            file = files[int(a)]
            validfile = True
        except (IndexError, ValueError):
            a = input('Enter a valid list number to load the selected file: ')
    content = open(file).readlines()
    for i, x in enumerate(content):
        content[i] = str(x).split(',')
        try:
            board.celllist[int(content[i][0])][int(content[i][1])].label = 0
        except ValueError:  # Checks for invalid points
            print('ERROR: The file must be a series of integer points'
                  ' on separate lines e.g. 3,1 .' +
                  'Only points of this format will be loaded')
        except KeyError:  # Checks for points outside board
            print('ERROR: The file contains points which are'
                  ' outside the visible board. Only points inside the board'
                  ' will be loaded. To possibly fix this in the future,'
                  ' increase your terminal size.')
    return board


def main():
    a = ''
    try:  # Checks that user is using a valid terminal
        rows, columns = os.popen('stty size', 'r').read().split()
    except ValueError:
        print('\033[91m'+'Please switch to a terminal rather than stdin to' +
              ' run this simulation' + '\033[0m')
        return 1
    print("Welcome to Conway's Game of Life in Python")
    while a.lower() != 'load' and a.lower() != 'random':
        a = input('To play from a random seed, type random. ' +
                  'To load, type load: ')
    if a.lower() == 'random':
        board = randomboard(rows, columns)
    else:
        board = loadboard(rows, columns)
    while a != '':
        a = input('\033[92m' +
                  'To begin the simulation, just press the ENTER KEY.' +
                  ' To pause the simulation, press the ENTER KEY.' +
                  '\033[0m')
    global terminal
    terminal = curses.initscr()  # Opens a curses window
    curses.noecho()
    curses.cbreak()
    terminal.nodelay(1)  # Don't wait for user input later
    while True:  # Runs simulation loop
        try:
            try:
                board.printboard()
            except curses.error:  # Checks for window resize errrors
                curses.endwin()  # Closes curses window
                input('\033[91m' +
                      'PAUSED: The window has been resized which can lead to' +
                      ' display errors. Please restore the window to its ' +
                      'original size and press the ENTER KEY to continue. ' +
                      '\033[0m')
                terminal = curses.initscr()  # Reopens a curses window
                terminal.nodelay(1)  # Don't wait for user input later
            c = terminal.getch()
            if c == 10:  # Checks for pause button
                print('\033[91m' +
                      'PAUSED: Press the ENTER KEY to continue. ' +
                      '\033[0m')
                c = 0
                while c != 10:  # Checks for continue button
                    c = terminal.getch()
                curses.endwin()
                terminal = curses.initscr()  # Reopens a curses window
                terminal.nodelay(1)  # Don't wait for user input later
            board.updateboard()
        except KeyboardInterrupt:  # Ends program with KeyboardInterrupt
            break
    # Closes curses window
    curses.endwin()


if __name__ == "__main__":
    main()
