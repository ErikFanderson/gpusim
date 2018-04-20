

class node:
    '''
    Node represents gpu
    '''
    def __init__(self,nodeId):
        '''
        node has links (outgoing) with diff BWs associated with each link
        '''
        self.nodeId = nodeId
        self.links = {}

    def addLink(self,downstreamNodeId,bw):
        '''
        adds outgoing link to node w/ specified BW
        '''
        self.links[downstreamNodeId] = bw
