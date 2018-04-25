from topology import topology
from trafficManager import *
from traceGen import *
import globals
import timing

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

    ###########################################################################################
    TM1 = trafficManager("./traceFiles/traceTest",topology("./connectionFiles/connectionFile"),1)
    ###########################################################################################

    ###########################################################################################
    #TM2 = TM1.genOptimizedTopology("./connectionFiles/connectionsOptimized_25GB",1)
    ###########################################################################################

    ###########################################################################################
    #TM3 = TM1.genOptimizedTopology("./connectionFiles/connectionsOptimized_12_5GB",2)
    ###########################################################################################

    ###########################################################################################
    #TM4 = TM1.genOptimizedTopology("./connectionFiles/connectionsOptimized_6_25GB",4)
    ###########################################################################################

    ###########################################################################################
    #TM5 = TM1.genOptimizedTopology("./connectionFiles/connectionsOptimized_3_125GB",8)
    ###########################################################################################

    RTLList = []
    scalerList = range(3)
    for i in scalerList:
        scalerList[i] = pow(2,i)
        TM_opt = TM1.genOptimizedTopology("./connectionFiles/connectionsOptimized_"+str(scalerList[i]),scalerList[i])
        RTLList.append(TM_opt.printRTL())
    #print "num RTLs: " + str(globals.numRTLs)
    #plt.figure(globals.figureNum)
    #plt.plot(scalerList,cycleList,'*-')
    #plt.gca().invert_yaxis()
    #plt.title("Traffic Matrix")
    #plt.xlabel("Scaler Value")
    #plt.ylabel("Total RTL")
    #globals.figureNum += 1

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
    #TM1.printCycles()
    #TM2.printCycles()
    #TM1.printTrafficMatrix()
    #TM1.topology.printConnectivity()
    #TM2.topology.printConnectivity()
    #TM3.topology.printConnectivity()
    #TM4.topology.printConnectivity()
    #TM5.topology.printConnectivity()
    #plt.show()
