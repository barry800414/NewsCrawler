#!/usr/bin/env python3 

'''
This codes implements the function of converting
a list of typed denpendencies to dependency graph for 
later usage.
Author: Wei-Ming Chen
Date: 2015/03/07
Last Update: 2015/03/08
'''
import json
import networkx as nx

class DepTree():
    # tdList: the list of typed dependencies
    def __init__(self, tdList):
        self.t = nx.DiGraph()
        self.rootId = -1
        if tdList != None:
            for dep in tdList:
                # relation, govPos, govWord, govTag, depPos, depWord, depTag
                (rel, gP, gW, gT, dP, dW, dT) = dep.split(" ")
                # skip root node in typed dependency list, using the child or root
                if gW == 'ROOT':
                    self.rootId = dP
                    self.add_node(dP, word=dW, tag=dT)
                    continue
                self.t.add_edge(gP, dP, rel=rel, gone=False)
                self.t.add_node(gP, word=gW, tag=gT)
                self.t.add_node(dP, word=dW, tag=dT)
            self.reset()
        self.nowNodes = None
        self.allowedGov = None
        self.allowedDep = None

    def isValid(self):
        if self.rootId == -1:
            return False
        else:
            return True

    def add_node(self, nodeId, word, tag):
        self.t.add_node(nodeId, word=word, tag=tag)

    def add_edge(self, govNodeId, depNodeId, rel, gone=False):
        self.t.add_edge(govNodeId, depNodeId, rel=rel, gone=gone)

    '''
    add allowed node word/tags or now words for further usage
    type: the type of allowed words/tags or now words to be added
        [t][w]: d[t] is a set of allowed words of POS-tag t
        [w][t]: d[w] is a set of allowed tags of word w
        (w, t): d is a set of pairs (w,t), which means word w with tag 
                t is allowed
        word: d is a set of words, which means all words (regardless of 
              their POS-tags) in this set are allowed 
        tag: d is a set of tags, which means all tags (regardless of the
             word) in this set are allowed
        all: all tags and words are allowed
    setType: the type of target set
        nowNodes: the selected words in this step
        allowedGov: the allowed words(from, gov) in this step
        allowedDep: the allowed words(to, dep) in this step
    '''
    def __addNodeSet(self, wtSet, type, setType):
        # the set of nodes to be the source of extraction 
        if setType == 'nowNodes':
            toAdd = self.nowNodes
        # the set of allowed Gov nodes for extraction
        elif setType == 'allowedGov':
            toAdd = self.allowedGov
        # the set of allowed Dep nodes for extraction
        elif setType == 'allowedDep':
            toAdd = self.allowedDep

        if type == '[t][w]':
            for n in self.t.nodes(data=True):
                if n[1]['tag'] in wtSet:
                    if n[1]['word'] in wtSet[n[1]['tag']]:
                        toAdd.add(n[0])
        elif type == '[w][t]':
            for n in self.t.nodes(data=True):
                if n[1]['word'] in wtSet:
                    if n[1]['tag'] in wtSet[n[1]['word']]:
                        toAdd.add(n[0])
        elif type == '(w,t)':
            for n in self.t.nodes(data=True):
                if (n[1]['word'], n[1]['tag']) in wtSet:
                    toAdd.add(n[0])
        elif type == 'word':
            for n in self.t.nodes(data=True):
                if n[1]['word'] in wtSet:
                    toAdd.add(n[0])
        elif type == 'tag':
            for n in self.t.nodes(data=True):
                if n[1]['tag'] in wtSet:
                    toAdd.add(n[0])
        elif type == 'pos':
            toAdd.update(wtSet)

    # clean the original set, then add the given set to them
    def __setNodeSet(self, wtSet, type, setType):
        if setType == 'nowNodes':
            self.nowNodes = set()
        elif setType == 'allowedGov':
            self.allowedGov = set()
        elif setType == 'allowedDep':
            self.allowedDep = set()
        self.__addNodeSet(wtSet, type, setType)

    def addNowWord(self, wtSet, type='[t][w]'):
        self.__addNodeSet(wtSet, type, setType='nowNodes')

    def addAllowedGovWord(self, wtSet, type='[t][w]'):
        self.__addNodeSet(wtSet, type, setType='allowedGov')

    def addAllowedDepWord(self, wtSet, type='[t][w]'):
        self.__addNodeSet(wtSet, type, setType='allowedDep')

    def setNowWord(self, wtSet, type='[t][w]'):
        self.__setNodeSet(wtSet, type, setType='nowNodes')

    def setAllowedGovWord(self, wtSet, type='[t][w]'):
        self.__setNodeSet(wtSet, type, setType='allowedGov')

    def setAllowedDepWord(self, wtSet, type='[t][w]'):
        self.__setNodeSet(wtSet, type, setType='allowedDep')

    def setAllowedRel(self, relSet):
        if relSet != None:
            self.allowedRel = set(relSet)
        else:
            self.allowedRel = None

    def addAllowedRel(self, relSet):
        self.allowedRel.update(relSet)

    # FIXME: does dep graph contain cycle? avoid node repeat?
    def searchOneStep(self, keepDirection=False):
        edgeList = list()
        # out edges
        for e in self.t.out_edges(self.nowNodes, data=True):
            if self.__evalEdge(e, 'dep'):
                self.t.edge[e[0]][e[1]]['gone'] = True
                rel = e[2]['rel']
                sP = e[0] 
                sW = self.t.node[e[0]]['word']
                sT = self.t.node[e[0]]['tag']
                eP = e[1]
                eW = self.t.node[e[1]]['word']
                eT = self.t.node[e[1]]['tag']
                edgeList.append((rel, sP, sW, sT, eP, eW, eT))
                
        # in edges
        edgeList = list()
        for e in self.t.in_edges(self.nowNodes, data=True):
            if self.__evalEdge(e, 'gov'):
                self.t.edge[e[0]][e[1]]['gone'] = True
                rel = e[2]['rel']
                if keepDirection:
                    sP = e[1] 
                    sW = self.t.node[e[1]]['word']
                    sT = self.t.node[e[1]]['tag']
                    eP = e[0]
                    eW = self.t.node[e[0]]['word']
                    eT = self.t.node[e[0]]['tag']
                else:
                    sP = e[0] 
                    sW = self.t.node[e[0]]['word']
                    sT = self.t.node[e[0]]['tag']
                    eP = e[1]
                    eW = self.t.node[e[1]]['word']
                    eT = self.t.node[e[1]]['tag']
                edgeList.append((rel, sP, sW, sT, eP, eW, eT))


        # s: starting (maybe dep or gov node)
        # e: ending(maybe dep or gov node)
        return edgeList

    # search edges which matching 
    def searchOneStepNoExchange(self):
        edgeList = list()
        # out edges
        for e in self.t.out_edges(self.nowNodes, data=True):
            if self.__evalEdge(e, 'dep'):
                self.t.edge[e[0]][e[1]]['gone'] = True
                rel = e[2]['rel']
                sP = e[0] 
                sW = self.t.node[e[0]]['word']
                sT = self.t.node[e[0]]['tag']
                eP = e[1]
                eW = self.t.node[e[1]]['word']
                eT = self.t.node[e[1]]['tag']
                edgeList.append((rel, sP, sW, sT, eP, eW, eT))
                
        # in edges
        edgeList = list()
        for e in self.t.in_edges(self.nowNodes, data=True):
            if self.__evalEdge(e, 'gov'):
                self.t.edge[e[0]][e[1]]['gone'] = True
                rel = e[2]['rel']
                sP = e[1] 
                sW = self.t.node[e[1]]['word']
                sT = self.t.node[e[1]]['tag']
                eP = e[0]
                eW = self.t.node[e[0]]['word']
                eT = self.t.node[e[0]]['tag']
                edgeList.append((rel, sP, sW, sT, eP, eW, eT))
        # s: starting (maybe dep or gov node)
        # e: ending(maybe dep or gov node)
        return edgeList


    # evaluate whether the edge can be used, only the edges
    # which obey the allowing rules can be used.
    def __evalEdge(self, edge, target):
        if edge[2]['gone']:
            return False
        n1 = edge[0]
        n2 = edge[1]
        rel = edge[2]['rel']
        if self.allowedRel != None:
            if rel not in self.allowedRel:
                return False
        if target == 'dep' or target == 'to':
            if self.allowedDep != None:
                if n2 not in self.allowedDep:
                    return False
        elif target == 'gov' or target == 'from':
            if self.allowedGov != None:
                if n1 not in self.allowedGov:
                    return False
        else:
            return False
        return True
            
    # reset the dep graph to initial status
    def reset(self):
        for e in self.t.edges():
            self.t.edge[e[0]][e[1]]['gone'] = False
        self.nowNodes = set()
        self.allowedGov = set()
        self.allowedDep = set()
        self.allowedRel = set()

    def nodes(self, data=False):
        return self.t.nodes(data=data)

    def edges(self, data=False):
        return self.t.edges(data=data)

    def getSepStr(self, wordSep=' '):
        outStr = ''
        for n in sorted(self.t.nodes()):
            if len(outStr) == 0:
                outStr = self.t.node[n]['word']
            else:
                outStr += wordSep + self.t.node[n]['word']
        return outStr

    def getStr(self):
        return self.getSepStr(wordSep='')

    def __repr__(self):
        obj = dict()
        obj['nodes']= self.t.nodes(data=True)
        obj['edges'] = self.t.edges(data=True)
        obj['nowNodes'] = self.nowNodes
        obj['allowedGovNodes'] = self.allowedGov
        obj['allowedDepNodes'] = self.allowedDep
        return json.dumps(obj)

        outStr = 'Nodes:'
        for n in self.t.nodes(data=True):
            outStr += str(n) + ','
        outStr += 'Edges:'
        for e in self.t.edges(data=True):
            outStr += str(e) + ','
        
        return outStr

