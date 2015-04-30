
import json
import sys
from collections import defaultdict
import DepTree as DT
import TreePattern as TP

class NegPattern():
    # opn: opinion word, neg: negation word
    # rel: allowed negation relation types bewtween opinion word and negation word
    # negWord: allowed words of negation words e.g. bu, mei-yu 
    # opnWord: allowed words of opinion words
    # opnNodeType: the type of target opinion word (gov/dep)
    # opnTag: allowed tags of target opinion word
    # opnType: allowed usage of target opinion word in pattern tree, 
    #         typically it is 'opinion'
    def __init__(self, config):
        self.rel = set(config['rel']) if config['rel'] != None else None
        self.negWord = set(config['neg_word'])
        self.opnWord = set(config['opn_word']) if config['opn_word'] != None else None
        self.opnNodeType = config['opn_node_type']
        self.opnTag = set(config['opn_tag']) if config['opn_tag'] != None else None
        self.opnType = set(config['opn_type']) if config['opn_type'] != None else None
    
    # check whether the negation pattern can be found in dependency tree
    # tTree: target dependency tree (type: DepTree)
    # pTree: pattern tree (type: TreePattern)
    # mapping: a dict a->b, a is node id in tTree, b is node id in pTree,
    #          it should be fully matched
    def check(self, tTree, pTree, mapping):
        negCntDict = defaultdict(int)
        for pn in pTree.p.nodes():
            if self.isOpnNode(pTree.p.node[pn]):
                negCnt = self.getNegCnt(tTree, mapping[pn])
                if negCnt > 0:
                    type = pTree.p.node[pn]['output_as']
                    negCntDict[type] += negCnt
        return negCntDict

    # to check whether the node is an opinion nodes
    def isOpnNode(self, node):
        if self.opnWord != None:
            if node['word'] not in self.opnWord:
                return False
        if self.opnTag != None:
            if node['tag'] not in self.opnTag:
                return False
        if self.opnType != None:
            if node['output_as'] not in self.opnType:
                return False
        return True

    # to count the number of negation words
    def getNegCnt(self, tTree, nodeId):
        if self.opnNodeType == 'gov':
            edges = tTree.t.out_edges(nodeId)
        elif self.opnNodeType == 'dep':
            edges = tTree.t.in_edges(nodeId)

        negCnt = 0
        for e in edges:
            if self.relIsAllowed(tTree.t.edge[e[0]][e[1]]):
                if self.isNegNode(tTree.t.node[e[1]]):
                    negCnt += 1
        return negCnt

    # to check whether the edge is allowed 
    def relIsAllowed(self, edge):
        if self.rel != None:
            if edge['rel'] not in self.rel:
                return False
        return True

    # to check whether is a negation node
    def isNegNode(self, node):
        if self.negWord != None:
            if node['word'] not in self.negWord:
                return False
        return True

def checkAllNegPattern(negPList, tTree, pTree, mapping):
    negCntDict = defaultdict(int)
    for negP in negPList:
        r = negP.check(tTree, pTree, mapping)
        for key, value in r.items():
            negCntDict[key] += value
    return negCntDict

def loadNegPatterns(filename):
    with open(filename, 'r') as f:
        negPatternConfigs = json.load(f)
    negPList = list()
    for config in negPatternConfigs:
        negPList.append(NegPattern(config))
    return negPList

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'NegPatternJson TreePatternJson', file=sys.stderr)
        exit(-1)
        
    negPatternFile = sys.argv[1]
    treePatternFile = sys.argv[2]

    negPList = loadNegPatterns(negPatternFile)
    pTreeList = TP.loadPatterns(treePatternFile)

    # case evaluation 
    from NLPToolRequests import *
    s = "我不支持核四"
    tdList = sendDepParseRequest(s)
    depTree = DT.DepTree(tdList)
    
    for pTree in pTreeList:
        results = pTree.match(depTree)
        for r in results:
            negCntDict = checkAllNegPattern(negPList, 
                    depTree, pTree, r['mapping'])
            r['neg'] = negCntDict
            print(results)

    

