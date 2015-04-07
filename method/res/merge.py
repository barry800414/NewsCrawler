
import sys
import codecs

if len(sys.argv) != 5:
    print('Usage:', sys.argv[0], 'posList negList mergeCSV inEncoding', file=sys.stderr)
    exit(-1)

posFile = sys.argv[1]
negFile = sys.argv[2]
outFile = sys.argv[3]
inEncoding = sys.argv[4]

posSet = set()
negSet = set()

with codecs.open(posFile, 'r', encoding=inEncoding) as f:
    for line in f:
        w = line.strip()
        if ',' in w or len(w) == 0:
            print('Invalid pos:', w)
        else:
            posSet.add(w)

with codecs.open(negFile, 'r', encoding=inEncoding) as f:
    for line in f:
        w = line.strip()
        if ',' in w or len(w) == 0:
            print('Invalid neg:', w)
        else:
            negSet.add(w)

intersect = posSet & negSet
posSet = posSet - intersect
negSet = negSet - intersect
print('#both pos & neg:', len(intersect))
print(intersect)
print('#pure pos:', len(posSet))
print('#pure neg:', len(negSet))
print('#total:', len(posSet) + len(negSet))

with open(outFile, 'w') as f:
    posList = sorted(list(posSet))
    negList = sorted(list(negSet))
    for w in posList:
        print(w, '1', sep=',', file=f)
    for w in negList:
        print(w, '-1', sep=',', file=f)

