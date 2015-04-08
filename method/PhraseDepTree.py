
import sys

'''
This module implements the class of Phrase dependency tree, 
which combine constituent parsing and dependency parsing.
Usage: 1. for extracting relation between opinion words and opinion targets
Last Update: 2015/04/08
'''

class PhraseDepTree:
    def __init__(self, depTree, phrases, wordSep=' '):
        self.depTree = depTree
        self.phrases = phrases
        self.wPMap = PhraseDepTree.genPhraseInvertedIndex(phrases, wordSep)
        self.phrasesWordSet = PhraseDepTree.genPhraseWordSet(phrases, wordSep)

        # initialization
        self.t = nx.DiGraph()     
        for n in self.depTree.nodes(data=True):
            self.t.add_node(n[0], word=n[1]['word'], tag=n[1]['tag'], inNodes=[n[0]], inEdges=list())
            
            if n[1]['tag'] == 'ROOT':
                rootId = n[0]

        for e in self.depTree.edges(data=True):
            self.t.add_edge(e[0], e[1], rel=e[2]['rel'])
        
        # recursively(pre-order) generate phrase dependency tree
        self.__genPhraseDepTree(rootId)


    def __phraseDepTree(self, rootId):
        rNode = self.t.node[rootId]
        rWord = rNode['word']
        pList = self.wPMap[rWord]
        print('#possible Phrases of %s: %d' % (rWord, len(pList)), file=sys.stderr)
        # FIXME: here I simply select the first one
        pi = pList[0]
        for e in self.t.out_edges(rootId):
            sNodeId = e[1]
            sNode = self.t.node[sNodeId]
            sWord = sNode['word']
            if sWord in self.phrasesWordSet[pi]:
                rNode['inNodes'].append(sNodeId)
                rNode['inEdges'].append((rootId, sNodeId))
                for e2 in self.t.out_edges(sNodeId, data=True):
                    self.t.add_edge(rootId, e2[1], rel=e2[2]['rel'])
                self.t.remove_edge(rootId, sNodeId)
                self.t.remove_node(sNodeId)
                rNode['phrase'] = True
        
        for e in self.t.out_edges(rootId):
            self.__phraseDepTree(e[1])

    # wPMap[w] is a list of phrase indices who has word w
    def genPhraseInvertedIndex(phrases, wordSep=' '):
        wPMap = dict()
        for i, phrase in phrases:
            for word in phrase.strip().split(wordSep):
                if word not in wPMap:
                    wPMap[word] = list()
                wPMap[word].append(i)
        return wPMap

    def genPhraseWordSet(phrases, wordSep=' '):
        return [set(phrase.strip().split(' ')) for phrase in phrases]

    def __repr__(self):
        outStr = 'Original Dependency Tree:\n'
        outStr += self.depTree
        outStr += '\nPhrases:\n'
        outStr += self.phrases
        outStr += '\nPhrase Dependency Tree:\n'
        outStr += 'Nodes:\n'
        for n in self.t.nodes(data=True):
            outStr += n + '\n'
        outStr += 'Edges:\n'
        for e in self.t.edges(data=True):
            outStr += e + '\n'
        return outStr
    
