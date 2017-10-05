#-------------------------------------------------------------------------------
# Name:        queen puzzle
# Purpose:
#
#
# Created:     9/2/2017
#-------------------------------------------------------------------------------
import numpy as np
import sys
import time
sys.path.append('../PythonUtilities/')
import LogHelper
import cProfile

#Start Log
LogHelper.Init('queenpuzzle')

ENABLEPROFILE = True
VERBOSE = False

SIZE = 8
TESTRANGE = False
STARTRANGE = 11
ENDRANGE = 12

if not TESTRANGE:
    STARTRANGE = SIZE
    ENDRANGE = SIZE

def log(message):
    LogHelper.write(message=message,bright=False,sublogger=False)

# States
# 0 = Default
# 1 = Queen
# 2 = Space threatened by another queen
# 3 = Space already tested and no solution found
OPEN = 0
QUEEN = 1
BLOCKED = 2
TESTED = 3

#Board characters
LS = u'\u2591'
DS = u'\u2593'
Q = u'\u004F'
B = u'\u0058'
Q2 = u'\u003C'
Q3 = u'\u003E'
B1 = u'\u005B'
B2 = u'\u005D'
Tested = '##'

# Check new solution against existing solutions to see if it
# is just a rotated or flipped version of an existing solution
# Returns true if duplicates found
def compareSolution(board):
    if VERBOSE:
        print("Comparing solutions")
    global solution
    duplicate = False
    for result in solution:
        if duplicate:
            break
        if VERBOSE:
            print("Variations of existing solutions")
            printNPBoard(np.flipud(result))
            printNPBoard(np.fliplr(result))
            printNPBoard(np.rot90(result,k=1))
            printNPBoard(np.rot90(result,k=2))
            printNPBoard(np.rot90(result,k=3))
        for rot in range(0,4):
            tempboard = np.rot90(result,k=rot)
            if np.array_equal(board,tempboard) and rot>0:
                if VERBOSE:
                    print("Duplicate of existing solution - Rot %s degrees" % (rot*90))
                    printNPBoard(tempboard,PrintClean=True)
                duplicate = True
                break
            tempboard2 = np.flipud(tempboard)
            if np.array_equal(board,tempboard2):
                if VERBOSE:
                    print("Duplicate of existing solution - Rot %s & Flip Up/Down" % (rot*90))
                    printNPBoard(tempboard2,PrintClean=True)
                duplicate = True
                break
            tempboard3 = np.flipud(tempboard)
            if np.array_equal(board,tempboard3):
                if VERBOSE:
                    print("Duplicate of existing solution - Rot %s & Flip Left/Right" % (rot*90))
                    printNPBoard(tempboard3,PrintClean=True)
                duplicate = True
                break
    return duplicate

def genNPFromList(resultlist):
    tempboard = np.zeros((SIZE,SIZE),dtype=np.int8)
    length = len(resultlist)-1
    for row in range(length):
        tempboard[row,resultlist[row]] = QUEEN
    tempboard[length,resultlist[length]] = TESTED
    return tempboard

# Will undo the board
# Defaults to undoing the last queen.
def undoLastPlacement():
    global board, lastrow, lastcol, LASTSOLUTIONFOUND

    tempboard = np.zeros((SIZE,SIZE),dtype=np.int8)
    for r in range(0,SIZE):
        for c in range(0,SIZE):
            if board[r,c] == QUEEN:
                tempboard[r,c] = QUEEN
                lastrow = r
                lastcol = c
            elif board[r,c] == TESTED:
                tempboard[r,c] = TESTED
    #Change the last QUEEN to TESTED
    tempboard[lastrow,lastcol] = TESTED
    if VERBOSE:
        print("Backtracking last queen placement")
        print("at row %s and col %s" % (lastrow,lastcol))
    # Remove all subsequent TESTED cells
    for r in range(lastrow+1,SIZE):
        for c in range(0,SIZE):
            if board[r,c] == TESTED:
                tempboard[r,c] = OPEN
    board = tempboard
    # if at the last cell in the first row, last solution is found
    if lastrow==0 and lastcol==(SIZE-1):
        print("Last solution")
        LASTSOLUTIONFOUND = True
        lastrow = SIZE
    return lastrow

def printAllSolutions(Log=False):
    global solution
    print("Printing All Solutions")
    i = 1
    for result in solution:
        log("Solution #%s" % (i))
        printNPBoard(result,PrintClean=True,Log=Log,Console=False)
        i += 1

# Clean all the debug info from the solution
# so it is only 0 or 1's left
def cleanSolution(nparray):
    for row in range(SIZE-1,-1,-1):
        for col in range (0,SIZE):
            if nparray[row,col] != QUEEN:
                nparray[row,col] = OPEN
    return nparray

def printNPBoard(nparray,PrintAxis=False,PrintClean=False,Log=False,Console=False):
    odd = False
    for row in range(SIZE-1,-1,-1):
        if PrintAxis:
            rowstring = str(row)+' '
        else:
            rowstring = ''
        if SIZE % 2 == 0:
            odd = not odd
        for col in range (0,SIZE):
            odd = not odd
            if nparray[row,col] == QUEEN:
                rowstring += Q3+Q2
            elif nparray[row,col] == BLOCKED and not PrintClean:
                rowstring += B1+B2
            elif nparray[row,col] == TESTED and not PrintClean:
                rowstring += Tested
            elif odd:
                rowstring += LS+LS
            else:
                rowstring += DS+DS
        if Log:
            log(rowstring)
        if Console:
            print(rowstring)
    rowstring = '  '
    if PrintAxis:
        for item in range(SIZE):
            rowstring += str(item)+" "
        if Log:
            log(rowstring)
        if Console:
            print(rowstring)
    if Console:
        print("\n")

def AnalyzeBlocked():
    global board
    for r in range(0,SIZE):
        for c in range(0,SIZE):
            if board[r,c] == QUEEN:
                for c2 in range(0,SIZE):
                    for r2 in range(r+1,SIZE):
                        if c2==c or c2==c+(r-r2) or c2==c-(r-r2):
                            board[r2,c2] = BLOCKED

def main():
    global board, solution, lastrow, lastcol, LASTSOLUTIONFOUND
    solution = [] # List of solutions
    LASTSOLUTIONFOUND = False

    for r in range(STARTRANGE,ENDRANGE+1):
        #global solution
        start_time=time.time() #taking current time as starting time
        SIZE = r
        print("\n**** Processing %s by %s board *****" % (SIZE,SIZE))
        solution = [] # List of np array solutions
        duplicate = 0 # Keep track of # of duplicate solutions
        lastrow = 0
        lastcol = 0
        board = np.zeros((SIZE,SIZE),dtype=np.int8)
        row = 0
        # only test the first half of the columns
        maxcol = int(round(SIZE/2))
        LASTSOLUTIONFOUND = False
        while not LASTSOLUTIONFOUND:
            SOLUTIONFOUND = False
            while row<SIZE:
                QUEENPLACED = False
                col = 0
                #firstrowhalfdone = False
                while col<SIZE:# and not firstrowhalfdone:
                    #if row == 0 and col>maxcol:
                    #    firstrowhalfdone = True
                    #    #SOLUTIONFOUND = True
                    if board[row,col] == OPEN and not QUEENPLACED:
                        if row==lastrow and col<lastcol:
                            pass
                        else:
                            if VERBOSE:
                                print("Placing queen")
                                print("in row %s and col %s" % (row,col))
                            board[row,col] = QUEEN
                            col = SIZE
                            QUEENPLACED = True
                            if row == (SIZE-1):
                                SOLUTIONFOUND = True
                    col += 1
                if not QUEENPLACED:
                    if VERBOSE:
                        print("Unable to place queen")
                    row = undoLastPlacement()
                    STUCK = True
                else:
                    row += 1
                if VERBOSE:
                    printNPBoard(board)
                    #input("Press Enter to continue...")
                AnalyzeBlocked()

            if SOLUTIONFOUND:
                if VERBOSE:
                    print("\n**************Solution Found **************************************")
                board = cleanSolution(board)
                #printNPBoard(board)
                if not(compareSolution(board)):
                    if VERBOSE:
                        print("Duplicate solution, not appending")
                    solution.append(board)
                    #printAllSolutions()
                else:
                    duplicate += 1
                print("%s By %s Board Solutions-> Unique=%s, Duplicate=%s" % (r,r,len(solution),duplicate))
                SOLUTIONFOUND = False
                row = undoLastPlacement()
                AnalyzeBlocked()
                if VERBOSE:
                    printNPBoard(board)
            else:
                print("No solution found")
            if VERBOSE:
                input("Press Enter to continue...")

        elapsed_time=time.time()-start_time #again taking current time - starting time
        if elapsed_time > 3600:
            elapsed_time = elapsed_time/3600
            timemessage = ("Elapsed Time= %s hours" % round(elapsed_time,3))
        elif elapsed_time > 60:
            elapsed_time = elapsed_time/60
            timemessage =("Elapsed Time= %s mins" % round(elapsed_time,3))
        else:
            timemessage =("Elapsed Time= %s secs" % round(elapsed_time,3))

        log("%s By %s Board Solutions-> Unique=%s, Duplicate=%s" % (r,r,len(solution),duplicate))
        log(timemessage)
        print("Last Solution Found")
        print(timemessage)
        printAllSolutions(Log=True)

        if VERBOSE:
            input("Press Enter to continue...")

if __name__ == '__main__':
    if ENABLEPROFILE:
        cProfile.run('main()',sort='time')
    else:
        main()
