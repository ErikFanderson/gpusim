from topology import topology
from trafficManager import *
from traceGen import *
import globals
import timing
import logParser

#To do
#3. Begin writing paper intro [NOW]
#4. Get traces from Jorge
#7. Generate cost model or something related to how much you should increase granularity before switch cost becomes prohibitive
#8. Write up for OI class

if __name__ == "__main__":
    #Initialize global variables and timing module
    globals.init()
    timing.init()
    ###########################################################################################
    #Generate Traces from topology - WILL ONLY GENERATE TRACE BETWEEN NODES THAT ARE CONNECTED IN NETWORK PASSED TO traceGen()
    #topo1 = topology("./connectionFiles/dgx1")
    #traceGen(filename="./traceFiles/traceTest",numPackets=1000,topology=topo1,guard=100)
    ###########################################################################################
    #traceFile = "cifar10_alexnet_parameterserver_6473"
    #traceFile = "cifar10_alexnet_replicated_6230"
    #traceFile = "cifar10_densenet40_k12_parameterserver_9336"
    #traceFile = "cifar10_densenet40_k12_replicated_9098"
    #traceFile = "cifar10_densenet100_k24_replicated_9562"
    #traceFile = "cifar10_nasnet_parameterserver_6880"
    #traceFile = "cifar10_nasnet_replicated_7504"
    #traceFile = "cifar10_resnet20_v2_parameterserver_8347"
    #traceFile = "cifar10_resnet20_v2_replicated_8127"
    #traceFile = "cifar10_resnet110_v2_replicated_8819"
    #traceFile = "cifar10_resnet110_v2_parameterserver_8564"
    #traceFile = "flowers_mobilenet_parameterserver_11251"
    traceFile = "flowers_mobilenet_replicated_10889"
    #traceFile = "flowers_vgg16_parameterserver_10212"
    #traceFile = "flowers_vgg16_replicated_9854"

    connectionFile = "p3_x16Large"
    #traceFile = "traceTest"
    #connectionFile = "dgx_1"
    #traceFile = "traceTest"
    ###########################################################################################
    #logParser.parseLog(3,traceFile + '.log')
    TM1 = trafficManager("./traceFiles/" + traceFile,topology("./connectionFiles/" + connectionFile),1)
    ####################### Initial Column-Level Scope RTL Optimization #######################
    cycleInit = TM1.printRTL()
    TM1.printTrafficMatrix()
    TM1.topology.printConnectivity()
    #print "%.3g" % globals.totalB + " Bytes"
    #Scan through optimizations with different BU granularity
    RTLList = []
    numPlots = 1
    scalerList = range(numPlots)
    for i in scalerList:
        scalerList[i] = pow(2,i)
        TM_opt = TM1.genOptimizedTopology("./connectionFiles/connectionsOptimized_"+str(scalerList[i]),scalerList[i])
        RTLList.append(TM_opt.printRTL())
        TM_opt.topology.printConnectivity()
        percentageDec = (cycleInit - RTLList[i])/cycleInit
        print "Percent RTL Decrease: " + str(percentageDec*100) + "%"
    ###########################################################################################


    #print "num RTLs: " + str(globals.numRTLs)
    #Print Optimizations for all plots!
    #plt.figure(globals.figureNum)
    #plt.plot(scalerList,cycleList,'*-')
    #plt.gca().invert_yaxis()
    #plt.title("Traffic Matrix")
    #plt.xlabel("Scaler Value")
    #plt.ylabel("Total RTL")
    #globals.figureNum += 1
    ###########################################################################################
    ###########################################################################################
    #TM1.printCycles()
    #TM2.printCycles()
    #TM3.printCycles()
    #TM4.printCycles()
    #TM5.printCycles()
    ###########################################################################################
    #TM1 = trafficManager("./traceFiles/traceTest",topology("./connectionFiles/connectionFile"))
    #TM1.genOptimizedTopology("./connectionFiles/connectionsOptimized",2)
    #TM2 = trafficManager("./traceFiles/traceTest",topology("./connectionFiles/connectionsOptimized"))
    ###########################################################################################
    #TM1.printRTL()
    #TM2.printCycles()
    #TM1.printTrafficMatrix()
    #TM1.topology.printConnectivity()
    #TM2.topology.printConnectivity()
    #TM3.topology.printConnectivity()
    #TM4.topology.printConnectivity()
    #TM5.topology.printConnectivity()
    # plt.show()
