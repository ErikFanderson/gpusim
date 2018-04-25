import matplotlib.pyplot as plt
import scipy.io
import numpy as np
import globals

class topology:
    def __init__(self,filename):
        '''
        topology represented by traffic matrix
        '''
        self.filename = filename
        #Populates connectivityMatrix,numSRC,numDEST,and srcDict
        self.populate()

    def populate(self):
        self.srcDict = {}
        self.connectivityMatrix = self.returnConnectivityMatrix()
        self.numSRC = self.connectivityMatrix.shape[0]
        self.numDEST = self.connectivityMatrix.shape[1]
        for j in range(self.numSRC):
            self.srcDict[j] = []
            for i in range(self.numDEST):
                if self.connectivityMatrix[i][j] > 0:
                        self.srcDict[j].append(i)

    def returnConnectivityMatrix(self):
        '''
        prints traffic matrix using matplotlib
        Normalizes the number of bytes sent along each channel by the max number of bytes sent across any one channel
        returns max value and trafficMatrix(numpy float64 array)
        '''
        numNode = 0
        connectionList = []
        f = open(self.filename,'r')
        for line in f:
            #capture non-commented portion of line and strip \n
            line = line.split('//')[0].strip().split(' ')
            if len(line) > 1:
                numNode += 1
        #Generate NxN matrix for network with N nodes
        connectivityMatrix = np.array([[0 for x in range(numNode)] for y in range(numNode)])
        #Parse through file one more time - Need to change this so parsing is done once...
        f.seek(0)
        for line in f:
            #capture non-commented portion of line and strip \n
            line = line.split('//')[0].strip().replace('(',' ').replace(')','').split(' ')
            if len(line) > 1:
                for i in range((len(line)-1)/2):
                    src = int(line[0])
                    dest = int(line[2*i+1])
                    bw = int(line[2*i+2])
                    connectivityMatrix[dest][src] = bw
        f.close()
        return connectivityMatrix

    def printConnectivity(self):
        '''
        prints connectivity matrix using matplotlib
        '''
        plt.figure(globals.figureNum)
        plt.imshow(self.connectivityMatrix, cmap=plt.cm.gray)
        plt.clim(0,self.connectivityMatrix[:,0].sum())
        plt.gca().invert_yaxis()
        plt.title("Connectivity Matrix: " + self.filename)
        plt.xlabel("Source ID")
        plt.ylabel("Destination ID")
        plt.colorbar()
        #Prints normalized matrix to .mat located in project directory
        scipy.io.savemat('C:\Users\\bnsc5\Documents\MatlabProjects\OpticalInterconnects\Project\\figure' + str(globals.figureNum), mdict={'figure' + str(globals.figureNum): self.connectivityMatrix})
        globals.figureNum += 1
