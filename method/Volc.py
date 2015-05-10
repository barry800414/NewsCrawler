
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
class Volc:
    def __init__(self):
        self.volc = dict()
        self.rVolc = list()

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
        self.setVolc(volc)

    def save(self, filename):
        with open(filename, 'w') as f:
            for w, i in sorted(self.volc.items(), key=lambda x:x[1]):
                print(w, i, sep=':', file=f)

    # index must be from 0 to n-1
    def checkVolc(volc):
        maxIndex = max(volc.values())
        return maxIndex == len(volc) - 1

    def setVolc(self, volc):
        if Volc.checkVolc(volc):
            self.volc = volc
            self.__genInverseVolc()
        else:
            print('Invalid Volcabulary', file=sys.stderr)

    def __genInverseVolc(self):
        self.rVolc = [list() for i in range(0, len(self.volc))]
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

    def __contains__(self, index):
        return (index in self.volc)

    def __len__(self):
        return len(self.volc)

    def getWord(self, index):
        wStr = ''
        for i, w in enumerate(self.rVolc[index]):
            if i != len(self.rVolc[index]) - 1:
                wStr = wStr + w + ';'
            else:
                wStr = wStr + w
        return wStr

    def getWordList(self, index):
        return self.rVolc[index]

    # DF: document frequency  word index -> #doc contain that word
    def shrinkVolcByDocF(self, DF, minCnt=0):
        if minCnt < 0:
            return DF

        # generate old word index to new word index mapping
        # and new document frequency list
        newMapping = dict()
        newDF = list()
        for wi in range(0, len(self.rVolc)):
            if DF[wi] > minCnt:
                newMapping[wi] = len(newMapping)
                newDF.append(DF[wi])

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

if __name__ == '__main__':
    v = Volc()
    
    v['aaa'] = 0
    v['bbb'] = 1
    v['ccc'] = 1
    v['ddd'] = 2
    v['eee'] = 2
    v['fff'] = 3
    
    print(v.getWord(0), v.getWord(1), v.getWord(2))
    print(len(v))
    
    docF = [0 for i in range(0, 4)]
    docF[0] = 0
    docF[1] = 2
    docF[2] = 1
    docF[3] = 3
    
    print(v.shrinkVolcByDocF(docF, -1))
    
    print(v.volc)
    print(v.rVolc)

