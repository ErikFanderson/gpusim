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
    prints original conenctivity matrix
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
    #traceGen('./traceFiles/3x3_trace',baseLineTopology,100,None)
    # TM_og = trafficManager('./traceFiles/3x3_trace',baseLineTopology,1)
    TM_og = trafficManager('./traceFiles/cifar10_alexnet_parameterserver_6473',baseLineTopology,1)
    TM_new = TM_og.genOptimizedTopologyTEST("./connectionFiles/connectionsOptimized_TEST",1)
