
import sys
import pylab
from collections import defaultdict

def readWordValue(filename):
    wordValue = dict()
    with open(filename, 'r') as f:
        for line in f:
            entry = line.strip().split(':')
            w = entry[0]
            try:
                v = int(entry[1])
            except:
                v = float(entry[1])
            wordValue[w] = v
    return wordValue

def toHist(wordValue):
    cnt = defaultdict(int)
    for w,v in wordValue.items():
        cnt[v] += 1
    return cnt

def plotHist(wordValue):
    values = list(wordValue.values())
    pylab.hist(values, 50)
    
if len(sys.argv) != 2:
    print('Usage:', sys.argv[0], 'WordCntfile', file=sys.stderr)
    exit(-1)

wordValue = readWordValue(sys.argv[1])
cnt = toHist(wordValue)
total = sum(cnt.values())
r = total
for v, c in sorted(cnt.items(), key=lambda x:x[0]):
    r = r - c
    print("%d %d %d %f" % (v, c, r, float(r)/total *100))
#plotHist(wordValue)
