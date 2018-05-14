#Randomly generates traces based off of network
import matplotlib.pyplot as plt
import scipy.io
import numpy as np
from copy import copy
from itertools import *
import globals
from topology import topology
import timing

class trafficManager:
    def __init__(self,filename,topology,scaler):
        '''
        initializes traffic manager object with a filename and network
        '''
        self.filename = filename
        self.topology = topology
        self.scaler = scaler
        self.srcDict,self.trafficMatrix = self.populate()
        self.dim = self.trafficMatrix.shape[0]
        assert(self.dim == self.topology.dim)
        for key, value in self.srcDict.iteritems():
            self.srcDict[key].sort()
        if cmp(self.srcDict,self.topology.srcDict) != 0:
            print "Traffic Matrix Not utilizing all connections"
        self.TM_Normalized = self.trafficMatrix/np.amax(self.trafficMatrix)

    def populate(self):
        '''
        returns traffic matrix and srcDict from trace file
        Normalizes the number of bytes sent along each channel by the max number of bytes sent across any one channel
        returns max value and trafficMatrix(numpy float64 array)
        '''
        srcDict = {}
        #Generate NxN matrix for network with N nodes
        for i in range(self.topology.dim):
            srcDict[i] = []
        trafficMatrix = np.array([[0 for x in range(self.topology.dim)] for y in range(self.topology.dim)],dtype=np.float_)
        #Read trace file and add up traffic per channel
        f = open(self.filename,'r')
        for i, line in enumerate(f):
            line = line.split(' ')
            if len(line)==5:
                #Rows are destinations. columns are sources
                trafficMatrix[int(line[3])][int(line[2])] += int(line[4])
                src = int(line[2])
                dst = int(line[3])
                if dst not in srcDict[src]:
                    srcDict[src].append(dst)
        f.close()
        return srcDict,trafficMatrix

    def printTrafficMatrix(self):
        '''
        prints traffic matrix using matplotlib
        Normalizes the number of bytes sent along each channel by the max number of bytes sent across any one channel
        returns max value and trafficMatrix
        '''
        plt.figure(globals.figureNum)
        plt.imshow(self.TM_Normalized, cmap=plt.cm.cool)
        plt.clim(0,1)
        plt.gca().invert_yaxis()
        plt.title("Traffic Matrix: " + self.filename)
        plt.xlabel("Source ID")
        plt.ylabel("Destination ID")
        plt.colorbar()
        globals.figureNum += 1

    def generateTrafficMat(self):
        '''
        generates .mat file for traffic amtrix in project directory
        '''
        #Prints normalized matrix to .mat located in project directory
        dict = {'data': self.TM_Normalized,'maxScale':1}
        scipy.io.savemat('/mnt/c/Users/bnsc5/Documents/MatlabProjects/OpticalInterconnects/Project/matrices/' + self.filename.split('/')[-1], mdict=dict)

    def generateConnectivityMat(self):
        '''
        generates .mat file for traffic amtrix in project directory
        '''
        #Prints normalized matrix to .mat located in project directory
        dict = {'data': self.topology.connectivityMatrix,'maxScale':self.topology.connectivityMatrix[:,0].sum()}
        scipy.io.savemat('/mnt/c/Users/bnsc5/Documents/MatlabProjects/OpticalInterconnects/Project/matrices/' + self.topology.filename.split('/')[-1], mdict=dict)

    def genOptimizedTopology(self,filename,scaler):
        '''
        Generates the optimized topology
        filename => File that new connections file will be written to
        '''
        newCM = copy(self.topology.connectivityMatrix)
        newCM = np.multiply(newCM,scaler)
        #Iterate through sources (columns)
        f = open(filename,'w')
        f.write("//Optimized Connections File\n//TraceFile: " + self.filename + '\n')
        for i in range(self.dim):
            newCM[:,i] = self.optimizeConnectivity(newCM[:,i],i)
            f.write(str(i))
            for j,element in enumerate(newCM[:,i]):
                if element != 0:
                    f.write(' ' + str(j) + '(' + str(element) + ')')
            f.write('\n')
        f.close()
        #
        return trafficManager(self.filename,topology(filename),scaler)

    def optimizeConnectivity(self,column,columnNum):
        '''
        returns the column but optimized by exhaustively calculating every
        n multichoose k where n is number of connected nodes and k is number of bw units available per node
        '''
        #########################################################################
        ##Generate a list of all possible columns for the nodes that source needs to connect to
        #save original column
        originalColumn = copy(column)
        testCM = copy(self.topology.connectivityMatrix)
        #Get number of bw units to allocate and a list with all (connected) nodes
        k = int(column.sum())
        nodes = self.srcDict[columnNum]
        #This is how many units you can allocate after allocating
        k -= len(nodes)
        columnList = []
        totalCombinations = combinations_with_replacement(nodes, k)
        for combination in totalCombinations:
            combination = list(combination)
            column = np.zeros(len(column)).astype(int)
            for node in combination:
                column[node] += 1
            columnList.append(column)
        #########################################################################

        ##########################################################################
        #Add 1 to each of the elements that are in the nodes list for each column
        for i,col in enumerate(columnList):
            for j,element in enumerate(column):
                if j in nodes:
                    columnList[i][j] += 1
        #########################################################################

        #########################################################################
        #Test each column and find the one that gives minimum cycles
        smallestCycles = None
        for col in columnList:
            testCM[:,columnNum] = col
            #cycle = self.calcCycles(self.trafficMatrix,testCM)
            cycle = self.calcRTLColumn(self.trafficMatrix,testCM,columnNum)
            if cycle != None:
                if cycle < smallestCycles or smallestCycles==None:
                    smallestCycles = cycle
                    column = col
        #########################################################################

        #########################################################################
        #If traffic matrix is empty for a given column then return original column
        if self.trafficMatrix[:,columnNum].sum() == 0:
            return originalColumn
        else:
            return column
        #########################################################################

    def calcRTL(self,trafficMatrix,connectivityMatrix):
        '''
        Very simplistic way to calculate the cycles requried to send all packets
        Just divides the total size of bytes seen on channel by the bw to get cycle num.
        Compare different topologies cycleNum together to figure out speed up
        Rewritten for using connectivity matrix
        '''
        #Total number of cycles
        cycles = 0
        for i in range(self.dim):
            for j in range(self.dim):
                if trafficMatrix[i][j] != 0:
                    if connectivityMatrix[i][j] != 0:
                        cycles += (trafficMatrix[i][j]/connectivityMatrix[i][j])*self.scaler
                        globals.totalB += trafficMatrix[i][j]
                    else:
                        print
                        print "ERROR: Nonzero traffic between GPUs without connection\n"
                        #nonzero traffic but no connectivity! Invalid thus return None
                        return None
        return cycles

    def calcRTLColumn(self,trafficMatrix,connectivityMatrix,columnNum):
        '''
        Very simplistic way to calculate the cycles requried to send all packets
        Just divides the total size of bytes seen on channel by the bw to get cycle num.
        Compare different topologies cycleNum together to figure out speed up
        Rewritten for just column! Optimize!
        '''
        #Total number of cycles for column
        cycles = 0
        for i in range(self.dim):
            if trafficMatrix[i][columnNum] != 0:
                if connectivityMatrix[i][columnNum] != 0:
                    cycles += (trafficMatrix[i][columnNum]/connectivityMatrix[i][columnNum])*self.scaler
                    #globals.numRTLs += 1
                else:
                    #nonzero traffic but no connectivity! Invalid thus return None
                    return None
        return cycles

    def printRTL(self):
        '''
        calls calc Cycles and prints result
        '''
        cycles = self.calcRTL(self.trafficMatrix,self.topology.connectivityMatrix)
        #print self.topology.connectivityMatrix
        print "Topology: " + self.topology.filename + "\nTraffic: " + self.filename + "\n\tRelative Transmission Latency: " + str(cycles) + ' [AU]\n'
        #for i in range(8):
            #print int(self.topology.connectivityMatrix[i,:].sum())
        return cycles

    def returnRTL(self):
        '''
        calls calc Cycles and prints result
        '''
        cycles = self.calcRTL(self.trafficMatrix,self.topology.connectivityMatrix)
        return cycles

##################################################################################################################################################
##################################################################################################################################################
#Below is buggy code that was supposed to be used to optimize connectivity w/o requiring additional receivers.
#Iterative method showed no reduction in RTL!!!
##################################################################################################################################################
##################################################################################################################################################
    def recursiveFuncColumn(self,count,srcOrder,currentMatrix):
        ### Exit Condition ###
        if count == self.dim:
            #Add 1 to each of the elements that are in the nodes list for each column

            # for i in range(self.dim):
            #     for j in range(self.dim):
            #         if j in self.srcDict[i]:
            #             currentMatrix[j,i] += 1

            #Check to see if matrix is duplicate
            if any((currentMatrix == x).all() for x in globals.matrices):
                globals.duplicates.append(currentMatrix)
            else:
                globals.matrices.append(currentMatrix)

            #print self.calcRTL(self.trafficMatrix,currentMatrix)
            #if RTLTemp < RTL_low:
            #    bestMatrix = matrix
            #    RTL_low = RTLTemp
            # globals.count += 1



            #print currentMatrix
            #print globals.count
            #print currentMatrix
            return
        else:
            rowList = []
            srcNum = srcOrder[count]
            nodes = self.srcDict[srcNum]
            k = int(self.topology.connectivityMatrix[:,srcNum].sum())
            k -= len(nodes)
            #Generate the rows that can still be allocated
            for i in range(self.dim):
                if (currentMatrix[i,:].sum() < k) and (i in nodes):
                    for j in range(k - currentMatrix[i,:].sum()):
                        rowList.append(i)
            #This is how many units you can allocate after looking at current matrix
            #Need to implement allocation using less than all of the available BUs!!
            if rowList:
                for combination in combinations(rowList, k):
                    combination = list(combination)
                    column = np.zeros(self.dim).astype(int)
                    for node in combination:
                        column[node] += 1
                    currentMatrix[:,srcNum] = column
                    self.recursiveFunc(count+1,srcOrder,copy(currentMatrix))
            #         #globals.count += 1
            else:
                self.recursiveFunc(count+1,srcOrder,copy(currentMatrix))
                #globals.count += 1

    def recursiveFunc(self,count,srcOrder,currentMatrix):
        '''
        Needs a list of of lists [[i1,j1],[i2,j2],etc...] so it knows how to progress (so it can skip evaluating 0 elements)
        Generate the list of lists from the srcDict starting at src = 0 and ending at src = self.dim-1
        '''
        ### Exit Condition ###
        if count == self.dim:
            #Add 1 to each of the elements that are in the nodes list for each column

            # for i in range(self.dim):
            #     for j in range(self.dim):
            #         if j in self.srcDict[i]:
            #             currentMatrix[j,i] += 1

            #Check to see if matrix is duplicate
            if any((currentMatrix == x).all() for x in globals.matrices):
                globals.duplicates.append(currentMatrix)
            else:
                globals.matrices.append(currentMatrix)

            #print self.calcRTL(self.trafficMatrix,currentMatrix)
            #if RTLTemp < RTL_low:
            #    bestMatrix = matrix
            #    RTL_low = RTLTemp
            # globals.count += 1



            #print currentMatrix
            #print globals.count
            #print currentMatrix
            return
        else:
            rowList = []
            srcNum = srcOrder[count]
            nodes = self.srcDict[srcNum]
            k = int(self.topology.connectivityMatrix[:,srcNum].sum())
            k -= len(nodes)
            #Generate the rows that can still be allocated
            for i in range(self.dim):
                if (currentMatrix[i,:].sum() < k) and (i in nodes):
                    for j in range(k - currentMatrix[i,:].sum()):
                        rowList.append(i)
            #This is how many units you can allocate after looking at current matrix
            #Need to implement allocation using less than all of the available BUs!!
            if rowList:
                for combination in combinations(rowList, k):
                    combination = list(combination)
                    column = np.zeros(self.dim).astype(int)
                    for node in combination:
                        column[node] += 1
                    currentMatrix[:,srcNum] = column
                    self.recursiveFunc(count+1,srcOrder,copy(currentMatrix))
            #         #globals.count += 1
            else:
                self.recursiveFunc(count+1,srcOrder,copy(currentMatrix))
                #globals.count += 1

    def genOptimizedTopologyTEST(self,filename,scaler):
        '''
        Generates the optimized topology
        filename => File that new connections file will be written to
        ONLY USE W/ SCALER EQUAL TO 1
        '''
        #for x in permutations(range(self.dim)):
        #    self.recursiveFunc(0,x,np.array([[0 for x in range(self.topology.dim)] for y in range(self.topology.dim)]))
        self.recursiveFunc(0,range(self.dim),np.array([[0 for x in range(self.topology.dim)] for y in range(self.topology.dim)]))
        print 'Total Unique Matrices:\t\t' + str(len(globals.matrices))
        print 'Total Duplicate Matrices:\t' + str(len(globals.duplicates))
        # newCM = copy(self.topology.connectivityMatrix)
        # newCM = np.multiply(newCM,scaler)
        # #Iterate through sources (columns)
        # newCM = self.optimizeMatrix()
        # f = open(filename + 'TEST','w')
        # f.write("//Optimized Connections File\n//TraceFile: " + self.filename + '\n')
        # for i in range(self.dim):
        #     f.write(str(i))
        #     for j,element in enumerate(newCM[:,i]):
        #         if element != 0:
        #             f.write(' ' + str(j) + '(' + str(element) + ')')
        #     f.write('\n')
        # f.close()
        # print globals.count
        #return trafficManager(self.filename,topology(filename),scaler)


    def optimizeMatrix(self):
        '''
        Ensures row and column totals add up to 6
        '''
        RTL_low = self.calcRTL(self.trafficMatrix,self.topology.connectivityMatrix)
        bestMatrix = self.topology.connectivityMatrix
        matrix = np.array([[0 for x in range(self.topology.numSRC)] for y in range(self.topology.numDEST)])
        #Generate all possible columns
        columnDict = {}
        for i in range(self.dim):
            columnDict[i] = self.genColumnList(i,6)
        counter = 0
        #iterate through all combinations of columns
        for col0 in columnDict[0]:
            for col1 in columnDict[1]:
                for col2 in columnDict[2]:
                    for col3 in columnDict[3]:
                        for col4 in columnDict[4]:
                            for col5 in columnDict[5]:
                                for col6 in columnDict[6]:
                                    for col7 in columnDict[7]:
                                        #counter += 1
                                        #if counter == 500000:
                                        #    print timing.now()
                                        check = 0
                                        matrix[:,0] = col0
                                        matrix[:,1] = col1
                                        matrix[:,2] = col2
                                        matrix[:,3] = col3
                                        matrix[:,4] = col4
                                        matrix[:,5] = col5
                                        matrix[:,6] = col6
                                        matrix[:,7] = col7
                                        for i in range(self.dim):
                                            if matrix[i,:].sum() > 6:
                                                check = 1
                                        if check == 0:
                                            globals.count += 1
                                            RTLTemp = self.calcRTL(self.trafficMatrix,matrix)
                                            if RTLTemp < RTL_low:
                                                bestMatrix = matrix
                                                RTL_low = RTLTemp
        print RTL_low
        return bestMatrix

    def genColumnList(self,columnNum,k):
        '''
        returns the column but optimized by exhaustively calculating every
        n multichoose k where n is number of connected nodes and k is number of bw units available per node
        '''
        #########################################################################
        ##Generate a list of all possible columns for the nodes that source needs to connect to
        #save original column
        #originalColumn = copy(column)
        #testCM = copy(self.topology.connectivityMatrix)
        #Get number of bw units to allocate and a list with all (connected) nodes
        #k = int(column.sum())
        nodes = self.srcDict[columnNum]
        #This is how many units you can allocate after allocating
        k -= len(nodes)
        columnList = []
        totalCombinations = combinations_with_replacement(nodes, k)
        for combination in totalCombinations:
            combination = list(combination)
            column = np.zeros(self.dim).astype(int)
            for node in combination:
                column[node] += 1
            columnList.append(column)
        #Add 1 to each of the elements that are in the nodes list for each column
        for i,col in enumerate(columnList):
            for j,element in enumerate(column):
                if j in nodes:
                    columnList[i][j] += 1

        return columnList
##################################################################################################################################################
##################################################################################################################################################
