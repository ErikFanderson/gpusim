#Randomly generates traces based off of network
import matplotlib.pyplot as plt
import numpy as np
from copy import copy
from itertools import *

class trafficManager:
    def __init__(self,filename,topology):
        '''
        initializes traffic manager object with a filename and network
        '''
        self.filename = filename
        self.topology = topology
        self.trafficMatrix = self.returnTrafficMatrix()
        self.numRows = self.trafficMatrix.shape[0]
        self.numCols = self.trafficMatrix.shape[1]
        self.TM_Normalized = self.trafficMatrix/np.amax(self.trafficMatrix)

    def returnTrafficMatrix(self):
        '''
        prints traffic matrix using matplotlib
        Normalizes the number of bytes sent along each channel by the max number of bytes sent across any one channel
        returns max value and trafficMatrix(numpy float64 array)
        '''
        #Generate NxN matrix for network with N nodes
        trafficMatrix = np.array([[0 for x in range(self.topology.numSRC)] for y in range(self.topology.numDEST)],dtype=np.float_)
        #Read trace file and add up traffic per channel
        f = open(self.filename,'r')
        for i, line in enumerate(f):
            line = line.split(' ')
            if len(line)==5:
                #Rows are destinations. columns are sources
                trafficMatrix[int(line[3])][int(line[2])] += int(line[4])
        f.close()
        return trafficMatrix

    def printTrafficMatrix(self):
        '''
        prints traffic matrix using matplotlib
        Normalizes the number of bytes sent along each channel by the max number of bytes sent across any one channel
        returns max value and trafficMatrix
        '''
        plt.imshow(self.TM_Normalized, cmap=plt.cm.hot)
        plt.clim(0,1)
        plt.gca().invert_yaxis()
        plt.title("Traffic Matrix")
        plt.xlabel("Source ID")
        plt.ylabel("Destination ID")
        plt.colorbar()
        plt.show()

    def genOptimizedTopology(self,filename):
        '''
        Generates the optimized topology
        filename => File that new connections file will be written to
        '''
        ######%%%%%%%%######
        newCM = copy(self.topology.connectivityMatrix)
        ######%%%%%%%%######
        #Iterate through sources (columns)
        f = open(filename,'w')
        f.write("//Optimized Connections File\n//TraceFile: " + self.filename + '\n')
        for i in range(self.topology.numSRC):
            newCM[:,i] = self.optimizeConnectivity(newCM[:,i],i)
            f.write(str(i))
            for j,element in enumerate(newCM[:,i]):
                if element != 0:
                    f.write(' ' + str(j) + '(' + str(element) + ')')
            f.write('\n')
        f.close()

    def optimizeConnectivity(self,column,columnNum):
        '''
        returns the column but optimized by exhaustively calculating every
        n multichoose k where n is number of nodes and k is number of bw units available per node
        '''
        #save original column
        originalColumn = copy(column)
        testCM = copy(self.topology.connectivityMatrix)
        #Get number ofbw units to allocate and a list with all nodes
        k = int(column.sum())
        nodes = range(self.topology.numDEST)
        #Generate a list of all possible columns
        columnList = []
        totalCombinations = combinations_with_replacement(nodes, k)
        for combination in totalCombinations:
            combination = list(combination)
            column = np.zeros(len(column)).astype(int)
            for node in combination:
                column[node] += 1
            columnList.append(column)
        #Test each column and find the one that gives minimum cycles
        smallestCycles = None
        for col in columnList:
            testCM[:,columnNum] = col
            cycle = self.calcCycles(self.trafficMatrix,testCM)
            if cycle != None:
                if cycle < smallestCycles or smallestCycles==None:
                    smallestCycles = cycle
                    column = col

        #If traffic matrix is empty for a given column then return original column
        if self.trafficMatrix[:,columnNum].sum() == 0:
            return originalColumn
        else:
            return column

    def calcCycles(self,trafficMatrix,connectivityMatrix):
        '''
        Very simplistic way to calculate the cycles requried to send all packets
        Just divides the total size of bytes seen on channel by the bw to get cycle num.
        Compare different topologies cycleNum together to figure out speed up
        Rewritten for using connectivity matrix
        '''
        #Total number of cycles
        cycles = 0
        for i in range(self.numRows):
            for j in range(self.numCols):
                #If i, destId, is in j, sourceId, links dict
                if trafficMatrix[i][j] != 0:
                    if connectivityMatrix[i][j] != 0:
                        cycles += trafficMatrix[i][j]/connectivityMatrix[i][j]
                    else:
                        #nonzero traffic but no connectivity! Invalid thus return None
                        return None
        return cycles

    def printCycles(self):
        '''
        calls calc Cycles and prints result
        '''
        cycles = self.calcCycles(self.trafficMatrix,self.topology.connectivityMatrix)
        print "Topology: " + self.topology.filename + "\nTraffic: " + self.filename + "\n\tArbitray Cycle Units: " + str(cycles) + '\n'
