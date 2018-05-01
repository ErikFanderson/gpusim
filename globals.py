#Just to keep track of the figure number for matplotlib

def init():
    #For printing figures with matplotlib
    global figureNum
    figureNum = 0
    #For the timing module
    global line
    line = "="*40
    global start
    #For verifying that the equation in report is correct
    global numRTLs
    numRTLs = 0
    #for keeping track of the total number of Bytes sent in trace file
    global totalB
    totalB = 0
    global count
    count = 0
