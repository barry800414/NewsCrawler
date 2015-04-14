
from collections import defaultdict
import math

'''
This module implements the class of Language Model.
This is a simple implementation without considering
memory allocation and smoothing.
Usage: 1. for filtering phrases candidates
Last Update: 2015/04/08
'''

# Language Model
class LM:
    #SENT_START = -1
    #SENT_END = -2

    # corsus: a list of sentences, a sentence is a list of words
    # n: number of gram
    # w2i: word to index (volcabulary)
    # i2w: index to word
    def __init__(self, corpus, n=2, w2i=None, i2w=None):
        self.corpus = corpus
        self.n = n
        if w2i==None or i2w==None:
            self.w2i = dict()
            self.i2w = list()
        else:
            self.w2i = w2i
            self.iw2 = i2w
        
        self.nTokens = 0
        self.nGramCnt = [defaultdict(int) for i in range(0, self.n)]
        self.nGramLogProb = [dict() for i in range(0, self.n)]
        self.genNGramProb()

    def genNGramCount(self):
        for sent in self.corpus:
            self.nTokens += len(sent)
            seq = self.toIntSeq(sent)
            for n in range(1, self.n + 1):
                for i in range(0, len(seq) - n + 1):
                    self.nGramCnt[n-1][tuple(seq[i:i+n])] += 1

    def genNGramProb(self, smoothing=None):
        self.genNGramCount()
        
        # no smoothing
        for n in range(1, self.n + 1):
            if n == 1:
                self.nGramLogProb[0] = {w:math.log(float(cnt)/self.nTokens) for w, cnt in self.nGramCnt[0].items()}
            else:
                for seq, cnt in self.nGramCnt[n-1].items():
                    self.nGramLogProb[n-1][seq] = math.log(float(cnt) / self.nGramCnt[n-2][seq[0:-1]])
                
    def logProb(self, wordSeq):
        seq = self.toIntSeq(wordSeq)
        length = len(seq)
        logProb = 0.0
        for i, wi in enumerate(seq):
            if (i+1) <= self.n:
                refN = i+1
            else:
                refN = self.n
            logProb += self.nGramLogProb[refN-1][tuple(seq[i-refN+1:i+1])]
        return logProb

    def avgLogProb(self, wordSeq):
        logProb = self.logProb(wordSeq)
        return logProb / len(wordSeq)

    def toIntSeq(self, sentence):
        seq = list()
        #seq = [LM.SENT_START for i in range(0, self.n-1)]
        for w in sentence:
            if w not in self.w2i:
                self.w2i[w] = len(self.w2i)
                self.i2w.append(w)
            seq.append(self.w2i[w])
        #for i in range(0, self.n-1):
        #    seq.append(LM.SENT_END)
        return seq


def segNewsDictToCorpus(newsDict, wordSep=' ', sentSep=','):
    corpus = list()
    for newsId, news in newsDict.items():
        content = news['content_seg']
        for sent in content.split(','):
            corpus.append(sent.split(wordSep))
    return corpus

def constParsedNewsDictToCorpus(newsDict, wordSep=' '):
    corpus = list()
    for newsId, news in newsDict.items():
        for obj in news['content_constituent']:
            sent = obj['seg_sent']
            corpus.append(sent.split(wordSep))
    return corpus
            


'''#for debugging
corpus = [['This', 'is', 'a', 'test', 'sentence'], ['Today', 'is', 'good']]
n = 2
lm = LM(corpus, 2)

print(lm.nGramCnt)
print(lm.logProb(['This', 'is']))
'''
