from topology import topology
from trafficManager import *
from traceGen import *
import globals
import timing
import logParser
import os


def printTraffic(baselineConnections,dir):
    '''
    prints all traffic matrices as .mat files to matlab directory
    '''
    for filename in os.listdir(dir):
        if filename.endswith(".log"):
            TM_original = trafficManager("./traceFiles/" + filename.strip(".log"),topology("./connectionFiles/" + baselineConnections),1)
            TM_optimized = TM_original.genOptimizedTopology("./connectionFiles/connectionsOptimized_"+ filename.strip(".log"),1)
            #TM_optimized.topology.printConnectivity()
            TM_optimized.generateTrafficMat()

def printConnectivity(baselineConnections,dir,scaler):
    '''
    prints original connectivity matrix
    prints all optimized connectivity matrices for log files in dir.
    Prints => generates .mat file in matlab directory
    scaler is the multiplier for BUs (larger scaler => finer granularity of provisioning)
    '''
    #Create Lists for Data
    fileList = np.zeros((len(os.listdir(dir)),), dtype=np.object)
    percentageList = np.zeros((len(os.listdir(dir)),))
    #Run Optimization Algorithm
    baseLineTopology = topology("./connectionFiles/" + baselineConnections)
    for i,filename in enumerate(os.listdir(dir)):
        if filename.endswith(".log"):
            TM_original = trafficManager("./traceFiles/" + filename.strip(".log"),baseLineTopology,1)
            RTL_original = TM_original.returnRTL()
            TM_optimized = TM_original.genOptimizedTopology("./connectionFiles/connectionsOptimized_scaler" + str(scaler) + "_" +filename.strip(".log"),scaler)
            TM_optimized.generateConnectivityMat()
            percentageList[i] = ((RTL_original - TM_optimized.returnRTL())/RTL_original) * 100
            print filename.strip('log') + ': ' + str(percentageList[i]) + '% Decrease'
            fileList[i] = filename.strip(".log")
    #Generate mat for baseline topology
    TM_original.generateConnectivityMat()
    #Generate mat for percentage decrease data
    dict = {'filename': fileList,'percentDec':percentageList}
    scipy.io.savemat('/mnt/c/Users/bnsc5/Documents/MatlabProjects/OpticalInterconnects/Project/percentDec', mdict=dict)

if __name__ == "__main__":
    ################################################
    #Initialize global variables and timing module
    globals.init()
    timing.init()
    ################################################
    # baselineConnections = "p3_x16Large"
    # dir = './nvproflogs'
    # printTraffic(baselineConnections,dir)
    # #SCALER ONLY => (1,2,4,8)
    # printConnectivity(baselineConnections,dir,1)

    ##### TEST #####
    baseLineTopology = topology("./connectionFiles/p3_x16Large")
    TM_og = trafficManager('./traceFiles/cifar10_alexnet_parameterserver_6473',baseLineTopology,1)

    # baseLineTopology = topology("./connectionFiles/3x3")
    # traceGen('./traceFiles/3x3_trace',baseLineTopology,100,None)
    # TM_og = trafficManager('./traceFiles/3x3_trace',baseLineTopology,1)

    TM_new1 = TM_og.genOptimizedTopology_LIMIT("./connectionFiles/testTestTest1",1)
    # TM_new2 = TM_og.genOptimizedTopology_LIMIT("./connectionFiles/testTestTest2",2)
    #TM_new4 = TM_og.genOptimizedTopology_LIMIT("./connectionFiles/testTestTest4",4)

    print 'Original RTL:\t'+str(TM_og.returnRTL())
    print 'Optimized RTL:\t'+str(TM_new1.returnRTL()) + ' [Scaler: '+str(TM_new1.scaler)+']'
    # print 'Optimized RTL:\t'+str(TM_new2.returnRTL()) + ' [Scaler: '+str(TM_new2.scaler)+']'
    #print 'Optimized RTL:\t'+str(TM_new4.returnRTL()) + ' [Scaler: '+str(TM_new4.scaler)+']'

    #Print Graphs
    # TM_og.topology.printConnectivity()
    # TM_og.printTrafficMatrix()
    # TM_new.topology.printConnectivity()
    # plt.show()
