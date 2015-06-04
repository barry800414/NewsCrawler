
'''
The class of Vocabulary
File format:
word_or_phrase1: 0
word_or_phrase2: 1 
word_or_phrase3: 0 
...
phrase is a sequence of words separated by space

volc: word -> index
rVolc: index -> word string
'''

import sys
from collections import defaultdict
from misc import toStr

class Volc:
    def __init__(self):
        self.volc = dict() # word -> index (many-to-one)
        self.rVolc = list() # index words (one-to-many)
        self.lockVolc = False
        self.OOVDim = -1

    def load(self, filename):
        volc = dict()
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                entry = line.strip().split(':')
                if len(entry) != 2:
                    print('Line %d Error' % (i), file=sys.stderr)
                    continue
                w = entry[0]
                index = int(entry[1])
                if entry[0] not in volc:
                    volc[w] = index
                else:
                    print('Duplicated volcabulary %s in Line %d' % (entry[0], i), file=sys.stderr)
        #print(volc)
        self.setVolc(volc)

    def save(self, filename):
        with open(filename, 'w') as f:
            for w, i in sorted(self.volc.items(), key=lambda x:x[1]):
                print(w, i, sep=':', file=f)

    # the vocabulary will not be locked
    def copy(self):
        newVolc = Volc()
        newVolc.volc = dict(self.volc)
        newVolc.rVolc = list(self.rVolc)
        #newVolc.lockVolc = self.lockVolc
        newVolc.OOVDim = self.OOVDim
        return newVolc

    # index must be from 0 to n-1
    #def checkVolc(volc):
    #    maxIndex = max(volc.values())
    #    return maxIndex == len(volc) - 1
    def setVolc(self, volc):
        #if Volc.checkVolc(volc):
        self.volc = volc
        self.__genInverseVolc()
        #else:
        #    print('Invalid Volcabulary', file=sys.stderr)

    def __genInverseVolc(self):
        self.rVolc = [list() for i in range(0, max(self.volc.values())+1)]
        for w, i in self.volc.items():
            self.rVolc[i].append(w)

    def __getitem__(self, index):
        return self.volc[index]

    def __setitem__(self, index, value):
        if value > len(self.rVolc) - 1:
            rList = [list() for i in range(0, value - len(self.rVolc) + 1)]
            self.rVolc.extend(rList)
        self.rVolc[value].append(index)
        self.volc[index] = value

    def addWord(self, word):
        if word not in self.volc:
            if self.lockVolc:
                self.__setitem__(word, self.OOVDim)
            else:
                self.__setitem__(word, self.__len__())

    def __contains__(self, index):
        return (index in self.volc)

    def __len__(self):
        return len(self.rVolc)

    def getWord(self, index):
        wStr = ''
        for i, w in enumerate(self.rVolc[index]):
            if i != len(self.rVolc[index]) - 1:
                wStr = wStr + toStr(w, ensure_ascii=False) + ';'
            else:
                wStr = wStr + toStr(w, ensure_ascii=False)
        return wStr

    def getWordList(self, index):
        return self.rVolc[index]

    # when lock is True, all new words are viewed as OOV
    def lock(self):
        if self.OOVDim == -1:
            self.OOVDim = len(self.rVolc)
        self.lockVolc = True

    def unlock(self):
        self.lockVolc = False

    # DF: document frequency  word index -> #doc contain that word (defaultdict(int))
    # remove all words whose count less than minCnt
    def shrinkVolcByDocF(self, DF, minCnt=0):
        if minCnt < 0:
            return DF

        # generate old word index to new word index mapping
        # and new document frequency list
        newMapping = dict()
        newDF = defaultdict(int)
        for wi in range(0, len(self.rVolc)):
            if DF[wi] >= minCnt:
                newMapping[wi] = len(newMapping)
                newDF[len(newDF)] = DF[wi]

        # generate new volc
        newVolc = dict()
        for w, wi in self.volc.items():
            if wi in newMapping:
                newVolc[w] = newMapping[wi]
        
        # generate new inverse-volc
        newRVolc = [None for i in range(0, len(newMapping))]
        for oldWi, newWi in newMapping.items():
            newRVolc[newWi] = self.rVolc[oldWi]

        # set to the object variable
        self.volc = newVolc
        self.rVolc = newRVolc

        return newDF

    #FIXME: dealing with OOV problem
    def mergeVolc(volc1, volc2):
        if volc1 == None:
            if volc2 == None:
                return None
            else:
                return volc2.copy()
        else:
            if volc2 == None:
                return volc1.copy()
        newVolc = volc1.copy()
        offset = len(newVolc)
        for key, index in volc2.volc.items():
            if key not in newVolc.volc:
                newVolc[key] = index + offset
        return newVolc

# load volcabulary files from configuration
def loadVolcFileFromConfig(config):
    if config == None:
        return None
    volcDict = dict()
    for name, filename in config.items():
        v = Volc()
        v.load(filename)
        v.lock()
        volcDict[name] = v
    return volcDict

def testCase():
    v = Volc()
    v['aaa'] = 0
    v['bbb'] = 1
    v['ccc'] = 1
    v['ddd'] = 2
    v['eee'] = 2
    v['fff'] = 3
    v['zzz'] = len(v)
    print(v.getWord(0), v.getWord(1), v.getWord(2))
    print(len(v))
    
    print(v.volc)
    print(v.rVolc)
    docF = [0 for i in range(0, 5)]
    docF[0] = 0
    docF[1] = 2
    docF[2] = 1
    docF[3] = 3
    docF[4] = 5
    print(v.shrinkVolcByDocF(docF, 2))
    
    print(v.volc)
    print(v.rVolc)
    print(len(v))

    v2 = Volc()
    


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage:', sys.argv[0], 'volcFile', file=sys.stderr)
        exit(-1)
    
    volcFile = sys.argv[1]
    volc = Volc()
    volc.load(volcFile)

    print(len(volc))
    for i in range(0, len(volc)):
        print(volc.getWord(i))
