
import sys
import numpy as np
import json
from Volc import Volc
from ConvertWordVector import *

def filterByVolc(X, XVolc, inVolc):
    indexList = list()
    newVolc = Volc()
    for i in range(0, len(inVolc)):
        w = inVolc.getWord(i)
        if w in XVolc:
            indexList.append(XVolc[w])
            newVolc.addWord(w)
    newX = X[indexList]
    return (newX, newVolc)

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Usage:', sys.argv[0], 'InWordVectorFile(.vector) InVolcFile(.volc) OutWordVectorFile(.npy) OutNewVolc(.volc)', file=sys.stderr)
        print('\tConverting word vector file(text, from word2vec tool) to numpy array file(.npy), filtering words by inVolc', file=sys.stderr)
        exit(-1)

    inWVFile = sys.argv[1]
    inVolcFile = sys.argv[2]
    outWVFile = sys.argv[3]
    outVolcFile = sys.argv[4]
    
    print('Reading word vector file ...', file=sys.stderr)
    (volc, vectors) = readWordVector(inWVFile)
    print('Original volc size of word vector file:', len(volc))

    inVolc = Volc()
    inVolc.load(inVolcFile)
    print('Input volc size:', len(inVolc))

    (newX, newVolc) = filterByVolc(vectors, volc, inVolc)
    print('Output volc size:', len(newVolc))

    np.save(outWVFile, newX)
    newVolc.save(outVolcFile)


