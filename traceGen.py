from random import *

def traceGen(filename,topology,numPackets,guard):
    '''
    Randomly generates traces w/ minimum time interval, guard, between outgoing requests
    Trace Format => Epoch(optional) Delay SourceID DestID PacketSize(bytes)
    EPOCH => rReply,rRequest,wReply,wRequest
    PacketSize is anywhere from 1-18 Flits(16 bytes per Flit/Phit) 16-288 bytes
    '''
    f = open(filename,'w')
    for packetNum in range(numPackets):
        #Epoch
        f.write('EPOCH'+str(packetNum))
        #Delay
        f.write(' delay')
        #Source ID
        randNode = choice(topology.nodeList)
        f.write(' ' + str(randNode.nodeId))
        #Destination ID
        f.write(' ' + str(choice(list(randNode.links))))
        #Packet Size - Could create file with weighted distribution of sizes and then choose a random index to grab size from file
        f.write(' ' + str(randint(16,288)))
        f.write('\n')
    f.close()
