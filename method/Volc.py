
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
        self.volc = None
        self.rVolc = None

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
        if self.volc == None:
            return
        self.rVolc = [list() for i in range(0, len(self.volc))]
        for w, i in self.volc.items():
            self.rVolc[i].append(w)
        
        for i in range(0, len(self.rVolc)):
            wStr = ''
            for j, w in enumerate(self.rVolc[i]):
                if j != len(self.rVolc[i]) - 1:
                    wStr = wStr + w + ';'
                else:
                    wStr = wStr + w
            self.rVolc[i] = wStr

    def __getitem__(self, index):
        return self.volc[index]

    def getWord(self, index):
        return self.rVolc[index]

    

