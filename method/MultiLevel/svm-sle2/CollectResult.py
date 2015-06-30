
import sys, math

def readResult(filename):
    with open(filename, 'r') as f:
        for line in f:
           pass
        entry = line.strip().split(' ')
        score = float(entry[1])
    return score

def printTable(table, cRange, sizeRange):
    print('size:', end='')
    for size in sizeRange:
        print(size, end=' ')
    print('')
    for i, row in enumerate(table):
        print('C:', cRange[i], '|', sep='', end='')
        for v in row:
            print(' %.4f' % v, end='')
        print('')

seed = 1
cRange = [math.pow(2, i) for i in range(-5, 3)]
iter = 30
sizeRange = [20, 40, 60]

for t in [2, 3, 4, 5, 13]:
    scoreTable = [[0.0 for j in range(0, len(sizeRange))] for i in range(0, len(cRange))]
    for i, c in enumerate(cRange):
        for j, size in enumerate(sizeRange):
            avgScore = 0.0
            for fold in range(0, 10):
                resultFolder = './T%dS%dF%d_result' % (t, seed, fold)
                resultFile = '%s/T%dS%dF%d_C%f_iter%d_size%d' % (resultFolder, t, seed, fold, c, iter, size)
                avgScore += readResult(resultFile)
            avgScore /= fold
            scoreTable[i][j] = avgScore
    print('Topic %d:' % t)
    printTable(scoreTable, cRange, sizeRange)


