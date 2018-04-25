#Randomly generates traces based off of network
import matplotlib.pyplot as plt
import scipy.io
import numpy as np
from copy import copy
from itertools import *
import globals
from topology import topology

class trafficManager:
    def __init__(self,filename,topology,scaler):
        '''
        initializes traffic manager object with a filename and network
        '''
        self.filename = filename
        self.topology = topology
        self.scaler = scaler
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
        plt.figure(globals.figureNum)
        plt.imshow(self.TM_Normalized, cmap=plt.cm.gray)
        plt.clim(0,1)
        plt.gca().invert_yaxis()
        plt.title("Traffic Matrix: " + self.filename)
        plt.xlabel("Source ID")
        plt.ylabel("Destination ID")
        plt.colorbar()
        #Prints normalized matrix to .mat located in project directory
        scipy.io.savemat('C:\Users\\bnsc5\Documents\MatlabProjects\OpticalInterconnects\Project\\figure' + str(globals.figureNum), mdict={'figure' + str(globals.figureNum): self.TM_Normalized})
        globals.figureNum += 1

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
        for i in range(self.topology.numSRC):
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
        nodes = self.topology.srcDict[columnNum]
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
        for i in range(self.numRows):
            for j in range(self.numCols):
                if trafficMatrix[i][j] != 0:
                    if connectivityMatrix[i][j] != 0:
                        cycles += (trafficMatrix[i][j]/connectivityMatrix[i][j])*self.scaler
                    else:
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
        for i in range(self.numRows):
            if trafficMatrix[i][columnNum] != 0:
                if connectivityMatrix[i][columnNum] != 0:
                    cycles += (trafficMatrix[i][columnNum]/connectivityMatrix[i][columnNum])*self.scaler
                    globals.numRTLs += 1
                else:
                    #nonzero traffic but no connectivity! Invalid thus return None
                    return None
        return cycles

    def printRTL(self):
        '''
        calls calc Cycles and prints result
        '''
        cycles = self.calcRTL(self.trafficMatrix,self.topology.connectivityMatrix)
        print "Topology: " + self.topology.filename + "\nTraffic: " + self.filename + "\n\tRelative Transmission Latency: " + str(cycles) + ' [AU]\n'
        return cycles
