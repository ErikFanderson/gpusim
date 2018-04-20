import matplotlib.pyplot as plt
import numpy as np

class topology:
    def __init__(self,filename):
        '''
        topology represented by traffic matrix
        '''
        self.filename = filename
        #Populates connectivity matrix
        self.connectivityMatrix = self.returnConnectivityMatrix()
        self.numSRC = self.connectivityMatrix.shape[0]
        self.numDEST = self.connectivityMatrix.shape[1]

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
        plt.imshow(self.connectivityMatrix, cmap=plt.cm.hot)
        #print self.connectivityMatrix
        plt.clim(0,6)
        plt.gca().invert_yaxis()
        plt.title("Connectivity Matrix")
        plt.xlabel("Source ID")
        plt.ylabel("Destination ID")
        plt.colorbar()
        plt.show()
