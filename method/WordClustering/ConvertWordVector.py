
import sys
import numpy as np
from Volc import Volc
import WordTag

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
        i = 0
        while True:
            try:
                line = f.readline()
                if not line:
                    break
            except Exception as e:
                print('\nAt line %d' % i, e)
                line = f.readline()
                volcNum = volcNum - 1
                i = i + 1
                continue
            
            entry = line.strip().split(' ')
            if len(entry) != dim + 1:
                print(line)
                print(len(entry))
            assert len(entry) == dim + 1
            assert entry[0].strip() not in volc
            volc.addWord(entry[0].strip())
            vector = list()
            for j in range(1, len(entry)):
                vector.append(float(entry[j]))
            vectors.append(vector)
            i = i + 1
            if (i+1) % 10 == 0:
                print('%cProgress: (%d/%d)' % (13, i+1, volcNum), end='', file=sys.stderr)
           
    assert len(volc) == len(vectors)
    vectors = np.array(vectors, dtype=np.float64)
    return (volc, vectors)

# filter X by word set
def filterByWord(X, volc, wordSet):
    # some of words in wordSet may not be in volc(because less 5 times words 
    # are removed)
    indexList = sorted(list(set([volc[w] for w in wordSet if w in volc])))
    newX = X[indexList]
    
    oldNewMapping = { oldI:newI for newI, oldI in enumerate(indexList) }
    newVolc = Volc()
    for w in wordSet:
        if w in volc:
            newVolc[w] = oldNewMapping[volc[w]]
            #if not np.array_equal(newX[oldNewMapping[volc[w]]],X[volc[w]]):
            #    print('fail')

    #print(newX.shape, len(newVolc))
    return (newX, newVolc)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Converting word vector file(text, from word2vec tool) to volcabulary file(.volc) and numpy array file(.npy)', file=sys.stderr)
        print('Usage:', sys.argv[0], 'InWordVectorFile(text) OutWordVectorFile(npy) outVolcFile [inWordTagFile]', file=sys.stderr)
        exit(-1)

    inWVFile = sys.argv[1]
    outWVFile = sys.argv[2]
    outVolcFile = sys.argv[3]
    
    print('Reading word vector file ...', file=sys.stderr)
    (volc, vectors) = readWordVector(inWVFile)
    
    wordSet = None
    if len(sys.argv) == 5:
        # if input word-tag file was given, then only the words and word vector
        # in word-tag file are output 
        inWordTagFile = sys.argv[4]
        with open(inWordTagFile, 'r') as f:
            (wordTag, tagWord) = WordTag.loadWordTag(f)
        wordSet = set(wordTag.keys())
        print('#words in word tag file:', len(wordSet))
        
        #print(wordSet - set(volc.volc.keys()))
        (newX, newVolc) = filterByWord(vectors, volc, wordSet)
        print('#words in new volc:', len(newVolc))
    else:
        newX = vectors
        newVolc = volc

    np.save(outWVFile, newX)
    newVolc.save(outVolcFile)


