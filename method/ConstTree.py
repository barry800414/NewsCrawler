
import networkx as nx

# constituent tree data structure 
class ConstTree:
    def __init__(self, nodes, edges, rootId=0):
        self.g = networkx.DiGraph()
        for n in nodes:
            self.g.add_node(n[0], type=n[1], label=n[2])
        for e in edges:
            self.g.add_edge(e[0], e[1])
        self.rootId = rootId

        self.phraseHeight = 2

    # give maxHeight information for each node in trees
    def labelMaxHeight(self, nowId):
        if self.isLeaf(nowId):
            self.g.node[nowId]['maxHeight'] = 0
            return 0
        else:
            maxHeight = -1
            for e in self.g.out_edges(nowId):
                h = self.labelMaxHeight(e[1])
                if (h+1) > maxHeight:
                    maxHeight = (h+1)
            self.g.node[nowId]['maxHeight'] = maxHeight
            return maxHeight

    # get subtree of given root node id
    def getSubtree(self, nodeId, subTree):
        outEdges = self.g.out_edges(nodeId)
        if len(outEdges) == 0: #leaf node
            subTree.add_node(self.g.node[nodeId], 
                    type=self.g.node[nodeId]['type'], 
                    label=self.g.node[nodeId]['label'])
        else:
            for e in outEdges:
                subTree.add_edge(e[0], e[1])
                self.getSubTree(e[1], subTree)
        return subTree

    # return true if all grand children are leaves
    def grandChildrenAreLeaves(self, nodeId):
        l1Egdes = self.g.out_edges(nodeId)
        for e in l1Edges:
            if not self.childrenAreLeaves(e[1]):
                return False
        return True

    # return true if all children are leaves
    def childrenAreLeaves(self, nodeId):
        outEdges = self.g.out_edges(nodeId)
        if len(outEdges) != 0:
            for e in outEdges:
                if not self.isLeaf(e[1]):
                    return False
            return True
        else:
            return False

    # return true if the node is leaf
    def isLeaf(self, nodeId):
        return (len(self.g.out_edges(nodeId)) == 0)

    # get the phrase subtree of given labels and in second layer from leaves
    def getPhrases(self, allowedLabelSet=set(['NP', 'VP'])):
        self.labelMaxHeight()
        phrases = list()
        for n in self.g.nodes():
            if self.isPhraseCandidate(n, allowedLabelSet):
                phrases.append(self.getSubtree(n, nx.DiGraph()))
        return phrases    

    # to check whether subtree(phrase) is candidate or not
    def isPhraseCandidate(self, nodeId, allowedLabelSet):
        maxHeight = self.g.node[nodeId]['maxHeight']
        label = self.g.node[nodeId]['label']
        if maxHeight == self.phraseHeight and label in allowedLabelSet:
            if self.grandChildrenAreLeaves(nodeId):
                return True
        return False

    def printTree(tree, outfile=sys.stdout):
        pass
