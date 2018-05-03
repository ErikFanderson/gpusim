import atexit
from time import clock
import globals

def secondsToStr(t):
    '''
    translates seconds format to string
    '''
    return "%d:%02d:%02d.%03d" % \
        reduce(lambda ll,b : divmod(ll[0],b) + ll[1:],
            [(t*1000,),1000,60,60])

def log(s, elapsed=None):
    print globals.line
    print secondsToStr(clock()), '-', s
    if elapsed:
        print "Elapsed time:", elapsed
    print globals.line
    print

def endlog():
    end = clock()
    elapsed = end-globals.start
    log("End Program", secondsToStr(elapsed))

def now():
    return secondsToStr(clock())

def init():
    globals.start = clock()
    atexit.register(endlog)
    log("Start Program")
