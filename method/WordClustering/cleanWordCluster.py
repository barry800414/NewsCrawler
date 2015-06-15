import sys
import codecs

# read word clustering (by human), each line is a cluster, 
# words are separated by space
def readWCFile(filename, sep=' '):
    wordClusters = list()
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            entry = line.strip().split(sep)
            wordSet = set([e.strip() for e in entry if len(e.strip()) != 0])
            #print(wordSet)
            wordClusters.append(wordSet)
    return wordClusters

def findConfliction(wordClusters, remove=True):
    nClusters = len(wordClusters)
    conflictSet = set()
    for i in range(0, nClusters):
        for j in range(i+1, nClusters):
            intersect = wordClusters[i] & wordClusters[j]
            if len(intersect) != 0:
                print('Cluster %d & Cluster %d:' % (i, j), intersect)
            conflictSet.update(intersect)
            wordClusters[i].difference_update(intersect)
            wordClusters[j].difference_update(intersect)
    return conflictSet


def writeWCFile(wordClusters, filename, sep=','):
    with open(filename,'w') as f:
        for cluster in wordClusters:
            for i, w in enumerate(list(cluster)):
                if i == len(cluster) - 1:
                    print(w, end='', file=f)
                else:
                    print(w, end=sep, file=f)
            print('', file=f)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Usage:', sys.argv[0], 'InWordCluster sep(space/comma) OutWordCluster sep(space/comma)', file=sys.stderr)
        exit(-1)
    
    inFile = sys.argv[1]
    inSep = ' ' if sys.argv[2] == 'space' else ','
    outFile = sys.argv[3]
    outSep = ' ' if sys.argv[4] == 'space' else ','

    wordClusters = readWCFile(inFile, sep=inSep)
    findConfliction(wordClusters, remove=True)

    writeWCFile(wordClusters, outFile, sep=outSep)


