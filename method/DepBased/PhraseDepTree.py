
import sys
import json
import networkx as nx

from DepTree import DepTree

'''
This module implements the class of Phrase dependency tree, 
which combine constituent parsing and dependency parsing.
Usage: 1. for extracting relation between opinion words and opinion targets
Last Update: 2015/04/08
'''

class Phrase:
    # sepStr: the string of phraseList where each words are separated by wordSep
    # tag: the tag of phrase (e.g. NP, VP...)
    def __init__(self, sepStr, tag, wordSep=' '):
        self.sepStr = sepStr
        self.tag = tag
        self.wordSep = wordSep
        self.wordLength = len(sepStr.split(wordSep))
        self.wordSet = set(sepStr.split(wordSep))
    
    def hasWord(self, word):
        return word in self.wordSet
   
    def getWordLength(self):
        return self.wordLength

    def getTag(self):
        return self.tag
    
    def getWordSep(self):
        return self.wordSep

    def getWordSet(self):
        return self.wordSet

    def getSepStr(self):
        return self.sepStr

    def getStr(self):
        return self.sepStr.replace(self.wordSep, '')

    # check whether this phrase is a subphrase of another phrase
    def isSubPhraseOf(self, phrase):
        if self.wordSep == phrase.getWordSep():
            return phrase.getSepStr().find(self.sepStr) >= 0
        else:
            #replace original wordSep to myself wordSep
            sepStr = phrase.getSepStr().replace(phrase.getWordSep, self.wordSep)
            return sepStr.find(self.sepStr) >= 0

    # check whether the phrase is contained in this sentence
    def isContainedIn(self, sentence, wordSep=' '):
        if self.wordSep == wordSep:
            return sentence.find(self.sepStr) >= 0
        else:
            sepStr = sentence.replace(wordSep, self.wordSep)
            return sepStr.find(self.sepStr) >= 0

    def __repr__(self):
        return '[%s] %s' % (self.tag, self.getSepStr())


def loadPhraseFile(jsonFile, wordSep=' '):
    with open(jsonFile, 'r') as f:
        topicPhraseList = json.load(f)

    newDict = dict()
    for topicId, phraseDict in topicPhraseList.items():
        newDict[topicId] = list()
        for tag, phraseList in phraseDict.items():
            for i in range(0, len(phraseList)):
                # convert Phrase object
                newDict[topicId].append(Phrase(phraseList[i], tag, wordSep=' '))
    return newDict  # newDict[t]: the list of phrase objects of topic t           

def filterPhraseByTag(phraseList, allowedTag):
    newList = list()
    for phrase in phraseList:
        if phrase.getTag() in allowedTag:
            newList.append(phrase)
    return newList

class PhraseDepTree(DepTree):
    def __init__(self, tdList, phraseList, wordSep=' '):
        super(PhraseDepTree, self).__init__(tdList)
        # filter out impossible phrases
        self.phraseList = self.filterPhrases(phraseList)
        self.wPMap = PhraseDepTree.genPhraseInvertedIndex(self.phraseList, wordSep)
        #print('wPMap:', self.wPMap)
        for n in self.t.nodes():
            self.t.node[n]['innerDepTree'] = None

    def __initInnerDepTree(nodeId, node):
        tree = DepTree(None)
        tree.add_node(nodeId, word=node['word'], tag=node['tag'])
        return tree

    # construct the phrase dependency tree
    def construct(self):
        self.__constructPhraseDepTree(self.rootId)

    # recursively(pre-order) generate phrase dependency tree
    # rNode: current root node 
    # sNode: current child node of root node
    def __constructPhraseDepTree(self, rootId):
        rNode = self.t.node[rootId]
        rWord = rNode['word']
        
        # if root word is in some phrase, then try to merge nodes
        if rWord in self.wPMap:
            # possible phrases of this word
            pCandList = self.wPMap[rWord]
            print('#possible Phrases of %s: %d' % (rWord, len(pCandList)), file=sys.stderr)
            # FIXME: here I simply select the first one (the longest one)
            phrase = self.phraseList[pCandList[0]] 
            
            # merging nodes into a phrase node
            for e in self.t.out_edges(rootId, data=True):
                sNodeId = e[1]
                sNode = self.t.node[sNodeId]
                sWord = sNode['word']
                if phrase.hasWord(sWord):
                    rNode['tag'] = phrase.getTag()

                    # shrink the child node into root node's inner DepTree
                    if rNode['innerDepTree'] == None:
                        rNode['innerDepTree'] = PhraseDepTree.__initInnerDepTree(rootId, rNode)
                    rNode['innerDepTree'].add_node(sNodeId, word=sNode['word'], tag=sNode['tag'])
                    rNode['innerDepTree'].add_edge(rootId, sNodeId, rel=e[2]['rel'])

                    # give all edges of child node to root node
                    for e2 in self.t.out_edges(sNodeId, data=True):
                        self.t.add_edge(rootId, e2[1], rel=e2[2]['rel'])
                    self.t.remove_edge(rootId, sNodeId)
                    self.t.remove_node(sNodeId)
            # update the 'word' attribute of node
            rNode['word'] = rNode['innerDepTree'].getSepStr()

            # to check whether it complete the phrase
            if rNode['word'] != phrase.getSepStr():
                print('merged node words:', rNode['word'])
                print('phrase:', phrase.getSepStr())

        # for each child node, to repeat the same process
        for e in self.t.out_edges(rootId):
            self.__constructPhraseDepTree(e[1])

    def filterPhrases(self, phraseList):
        newList = list()
        sentence = self.getSepStr(wordSep=' ')
        for phrase in phraseList:
            if phrase.isContainedIn(sentence):
                newList.append(phrase)
        return newList

    # wPMap[w] is a list of phrase indices who has word w
    def genPhraseInvertedIndex(phraseList, wordSep=' '):
        wPMap = dict()
        for i, phrase in enumerate(phraseList):
            for word in phrase.getWordSet():
                if word not in wPMap:
                    wPMap[word] = list()
                wPMap[word].append(i)
        # sort the phrase candidate list by word length (descending order)
        for w in wPMap.keys():
            wPMap[w].sort(key=lambda x:phraseList[x].getWordLength(), reverse=True)
        return wPMap

    def __repr__(self):
        #outStr = 'Original Dependency Tree:\n'
        #outStr += str(self.depTree)
        outStr = "Sentence:" + self.getSepStr(wordSep=' ')
        outStr += '\nPhrases:'
        for p in self.phraseList:
            outStr += str(p) + ', '
        outStr += '\nPhrase Dependency Tree:\n'
        outStr += 'Nodes:\n'
        for n in self.t.nodes(data=True):
            outStr += str(n) + '\n'
        outStr += 'Edges:\n'
        for e in self.t.edges(data=True):
            outStr += str(e) + '\n'
        return outStr

if __name__ == '__main__':
    
    #testing data
    tdList = [
        "root 0 ROOT null 3 enjoyed VV", 
        "nsubj 3 enjoyed VV 1 We NN",
        "advmod 3 enjoyed VV 2 really VA",
        "partmod 3 enjoyed VV 4 using VV",
        "dobj 4 using VV 8 SD500 NR", 
        "det 8 SD500 NR 5 the DET",
        "nn 8 SD500 NR 6 Canon NR", 
        "nn 8 SD500 NR 7 PowerShot NR"
    ]
    phraseList = [ Phrase("really enjoyed using", "VP"), 
                   Phrase("the Canon", "NP"),
                   Phrase("the Canon PowerShot", "NP"),
                   Phrase("the Canon PowerShot SD500", "NP")]


    tree = PhraseDepTree(tdList, phraseList)
    print('Original Sentence:', tree.getSepStr())
    tree.construct()
    print(tree)

