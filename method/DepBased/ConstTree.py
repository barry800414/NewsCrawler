#!/usr/bin/env python3 

import sys
import networkx as nx
from PhraseDepTree import Phrase

# constituent tree data structure 
class ConstTree:
    def __init__(self, nodes, edges, rootId=0):
        self.t = nx.DiGraph()
        if nodes != None:
            for n in nodes:
                self.t.add_node(n[0], type=n[1], label=n[2])
        if edges != None:
            for e in edges:
                self.t.add_edge(e[0], e[1])
        self.rootId = rootId

        self.phraseHeight = 2

    def add_node(self, nodeId, type, label):
        self.t.add_node(nodeId, type=type, label=label)
    
    def add_edge(self, nodeId1, nodeId2):
        self.t.add_edge(nodeId1, nodeId2)

    def resetTree(self, tree, rootId):
        self.t = tree
        self.rootId = rootId

    # give maxHeight information for each node in trees
    def labelMaxHeight(self, nowId):
        if self.isLeaf(nowId):
            self.t.node[nowId]['maxHeight'] = 0
            return 0
        else:
            maxHeight = -1
            for e in self.t.out_edges(nowId):
                h = self.labelMaxHeight(e[1])
                if (h+1) > maxHeight:
                    maxHeight = (h+1)
            self.t.node[nowId]['maxHeight'] = maxHeight
            return maxHeight

    # get subtree of given root node id
    # subTree is the container to store the subtree
    def getSubTree(self, nodeId, subTree):
        subTree.add_node(nodeId, type=self.t.node[nodeId]['type'], 
                    label=self.t.node[nodeId]['label'])
        outEdges = self.t.out_edges(nodeId)
        if len(outEdges) == 0: #leaf node    
            return subTree
        else:
            for e in outEdges:
                subTree.add_edge(e[0], e[1])
                self.getSubTree(e[1], subTree)
        return subTree

    # return true if all grand children are leaves
    def grandChildrenAreLeaves(self, nodeId):
        l1Edges = self.t.out_edges(nodeId)
        for e in l1Edges:
            if not self.childrenAreLeaves(e[1]):
                return False
        return True

    # return true if all children are leaves
    def childrenAreLeaves(self, nodeId):
        outEdges = self.t.out_edges(nodeId)
        if len(outEdges) != 0:
            for e in outEdges:
                if not self.isLeaf(e[1]):
                    return False
            return True
        else:
            return False

    # return true if the node is leaf
    def isLeaf(self, nodeId):
        return (len(self.t.out_edges(nodeId)) == 0)

    # get the phrase subtree of given labels and in second layer from leaves
    def getPhraseTrees(self, allowedLabelSet=set(['NP', 'VP'])):
        self.labelMaxHeight(self.rootId)
        phrases = list()
        for n in self.t.nodes():
            if self.isPhraseCandidate(n, allowedLabelSet):
                phrases.append(self.getSubTree(n, ConstTree(None, None, n)))
        return phrases    

    # to check whether subtree(phrase) is candidate or not
    def isPhraseCandidate(self, nodeId, allowedLabelSet):
        maxHeight = self.t.node[nodeId]['maxHeight']
        label = self.t.node[nodeId]['label']
        if maxHeight == self.phraseHeight and label in allowedLabelSet:
            if self.grandChildrenAreLeaves(nodeId):
                return True
        return False

    # merge the words in a constituent tree
    def getWords(self, wordSep=' '):
        nodesList = sorted(self.t.nodes(data=True), key=lambda x:x[0])
        words = ''
        for n in nodesList:
            if n[1]['type'] == 'word':
                words += n[1]['label'] + wordSep
        return words.strip()

    # return the tag(label) of root node
    def getRootTag(self):
        return self.t.node[self.rootId]['label']

    def getPhrase(self, wordSep=' '):
        #print('word: %s  tag:%s' % (self.getWords(wordSep), self.getRootTag()))
        #print(Phrase(self.getWords(wordSep), self.getRootTag()))

        return Phrase(self.getWords(wordSep), self.getRootTag())

    def printTree(tree, outfile=sys.stdout):
        print('Root:', tree.t.node[tree.rootId], file=outfile)
        print('Nodes:', file=outfile)
        for n in tree.t.nodes(data=True):
            if n[0] != tree.rootId:
                print(n, file=outfile)
        print('Edges:', file=outfile)
        for e in tree.t.edges():
            print(e, file=outfile)




    
