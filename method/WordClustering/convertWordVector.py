
import sys
import numpy as np
from Volc import Volc

# converting word vector file(text, from word2vec tool)
# to python format (npy)

# read word vector(text file) from word2vec tool
def readWordVector(filename):
    volc = Volc()
    with open(filename, 'r') as f:
        line = f.readline()
        entry = line.strip().split(' ')
        volcNum = int(entry[0])
        dim = int(entry[1])
        vectors = list()
        for line in f:
            entry = line.strip().split(' ')
            assert len(entry) == dim + 1
            assert entry[0] not in volc
            volc[entry[0]] = len(volc)
            vector = list()
            for i in range(1, len(entry)):
                vector.append(float(entry[i]))
            vectors.append(vector)
    assert len(volc) == len(vectors)
    vectors = np.array(vectors, dtype=np.float64)
    return (volc, vectors)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage:', sys.argv[0], 'InWordVectorFile(text) OutWordVectorFile(npy) outVolcFile [inWordTagFile]', file=sys.stderr)
        exit(-1)

    inWVFile = sys.argv[1]
    outWVFile = sys.argv[2]
    outVolcFile = sys.argv[3]
    
    (volc, vectors) = readWordVector(inWVFile)
    
    if len(sys.argv) == 5:
        inWordTagFile = sys.argv[4]
        

    np.save(outWVFile, vectors)
    volc.save(volcFile)



