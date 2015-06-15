
import sys
from cleanWordCluster import *
from WordClustering import *

# merge one word clustering file into another
# one of them should be ground truth

# merge word clustering
def mergeWC(gtWC, wc):
    newWC = list()
    for i, cluster in enumerate(wc):
        newCluster = set(cluster)
        for j, gtCluster in enumerate(gtWC):
            intersect = gtCluster & cluster
            if len(intersect) != 0:
                print('GTCluster %d & cluster %d:' %(j,i), intersect, file=sys.stderr)
            newCluster.difference_update(intersect)
        if len(newCluster) != 0:
            newWC.append(newCluster)
    for gtCluster in gtWC:
        newWC.append(set(gtCluster))
    return newWC

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:', sys.argv[0], 'InGroundTruthWCFile InWCFile2 OutMergedWCFilePrefix', file=sys.stderr)
        exit(-1)

    inGTWCFile = sys.argv[1]
    inWCFile = sys.argv[2]
    outFilePrefix = sys.argv[3]

    gtWC = readWCFile(inGTWCFile, sep=',')
    wc = readWCFile(inWCFile, sep=',')

    mergedWC = mergeWC(gtWC, wc)
    with open(outFilePrefix + '.txt', 'w') as f:
        printWordCluster(mergedWC, outfile=f)
    with open(outFilePrefix + '.volc', 'w') as f:
        printWordClusterAsVolc(mergedWC, outfile=f)

