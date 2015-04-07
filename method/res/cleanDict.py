import sys

# return a dict (word -> sentiment score)
def readSentiDict(filename):
    sentiDict = dict()
    posSet = set()
    negSet = set()
    with open(filename, 'r') as f:
        for i, line in enumerate(f):
            entry = line.strip().split(',')
            if len(entry) != 2:
                print('Line %d format error:' %(i+1), entry, file=sys.stderr)
                continue
            w = entry[0]
            s = int(entry[1])
            sentiDict[w] = s
            if s > 0: 
                posSet.add(w)
            elif s < 0:
                negSet.add(w)

    dupSet = posSet & negSet
    for w in dupSet:
        del sentiDict[w]
    
    posSet = posSet - dupSet
    negSet = negSet - dupSet

    assert len(posSet) + len(negSet) == len(sentiDict)
    
    print("#both pos & neg:", len(dupSet))
    print(dupSet)
    print("#pure pos:", len(posSet))
    print("#pure neg:", len(negSet))
    print("#total:", len(sentiDict))
    
    return sentiDict


if len(sys.argv) != 3:
    print('Usage:', sys.argv[0], 'inDictCSV outDictCSV', file=sys.stderr)
    exit(-1)

inDictCSV = sys.argv[1]
outDictCSV = sys.argv[2]

sentiDict = readSentiDict(inDictCSV)

with open(outDictCSV, 'w') as f:
    posList = sorted([w for w, s in sentiDict.items() if s > 0])
    negList = sorted([w for w, s in sentiDict.items() if s < 0])
    for w in posList:
        print(w, sentiDict[w], sep=',', file=f)
    for w in negList:
        print(w, sentiDict[w], sep=',', file=f)

