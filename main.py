from node import node
from topology import topology
from trafficManager import *
from traceGen import *

#To do
#2. Deprecate the node structure and use just traffic/connectivity matrices [NOW]
#3. Begin writing paper intro [NOW]
#4. Get traces from Jorge
#5. Generate connections files that represent increased and decreased granularity of BW [NOW]
#6. Implement n multichoose k where n is not every node but every possible node (so really 4 multichoose k NOT 8 multichoose k) [NOW]
#7. Generate cost model or something related to how much you should increase granularity before switch cost becomes prohibitive
#8. Write up for OI class
#9. Consolidate calcycles and calcCyclesInternal and ad print cycles function


if __name__ == "__main__":
    ##Generate Topologies
    #Original Topology
    topo1 = topology("./connectionFiles/connectionFile")
    #Generate Traces from topology - WILL ONLY GENERATE TRACE BETWEEN NODES THAT ARE CONNECTED IN NETWORK PASSED TO traceGen()
    traceGen(filename="traceTest",numPackets=1000,topology=topo1,guard=100)
    #Create Traffic Manager from trace file and networks
    TM1 = trafficManager("./traceFiles/traceTest",topo1)
    #TM1.topology.printConnectivity()
    #Generate Optimized topology file
    TM1.genOptimizedTopology("./connectionFiles/connectionsOptimized")
    #Create optimized topology
    topo_opt = topology("./connectionFiles/connectionsOptimized")
    TM2 = trafficManager("./traceFiles/traceTest",topo_opt)
    #Print Results
    TM1.calcCycles()
    TM2.calcCycles()

    TM1.topology.printConnectivity()
    TM2.printTrafficMatrix()
    TM2.topology.printConnectivity()
