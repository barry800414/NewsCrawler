
import sys

def readCSV(filename, dataType=None):
    with open(filename, 'r') as f:
        line = f.readline() # first line: column name
        colNameMap = {c.strip():i for i, c in enumerate(line.strip().split(','))}

        data = list()
        for line in f:
            entry = line.strip().split(',')
            if dataType != None:
                assert len(dataType) == len(entry)
                row = list()
                for i, e in enumerate(entry):
                    if dataType[i] == 'int':
                        row.append(int(e))
                    elif dataType[i] == 'float':
                        row.append(float(e))
                    else:
                        row.append(e.strip())
            else:
                row = entry
            data.append(row)
    return (colNameMap, data)

# colNameMap: name -> index 
def sortByColumn(data, colNameMap, sortColumn, reverse=True):
    if sortColumn not in colNameMap:
        return data #do nothing
    else:
        data.sort(key=lambda x:x[colNameMap[sortColumn]], reverse=reverse)
    return data

def allowData(data, colNameMap, filterColumn, allow, type='string'):
    if filterColumn not in colNameMap:
        return data 

    ci = colNameMap[filterColumn]
    newData = None
    if type == 'string':
        newData = [row for row in data if row[ci].strip() in allow]
    elif type == 'int':
        if type(allow) == int: # single value
            newData = [row for row in data if row[ci] == allow]
        elif (type(allow) == tuple or type(allow) == list) and len(allow) == 2: #min max
            newData = [row for row in data if row[ci] >= allow[0] and row[ci] <= allow[1]]
    elif type == 'float':
        if type(allow) == float: # single value
            newData = [row for row in data if floatEq(row[ci], allow)]
        elif (type(allow) == tuple or type(allow) == list) and len(allow) == 2: #min max
            newData = [row for row in data if row[ci] >= allow[0] and row[ci] <= allow[1]]
    return newData


def floatEq(f1, f2):
    return fabs(f1 - f2) < 1e-10

# f1Rows: topic -> row of self-train to self-test
# f2Row: all train all test
# f3Rows: topic -> row of leave one test
def printResultSummary(topicList, f1Rows, f2Row, f3Rows, colNameMap, scoreName, outfile=sys.stdout):
    print('TopicId, Self-TrainTest(%s), LeaveOneTest(%s), All-TrainTest(%s)' % (scoreName, scoreName, scoreName), file=outfile)
    si = colNameMap['MacroF1']
    for t in topicList:
        print(f1Rows[t])
        print(f3Rows[t])
        #print('%d, %f, %f, ' % (t, f1Rows[t][si], f3Rows[t][si]), file=outfile)
    print(f2Row[si])
    #print('All,         ,         , %f' % f2Row[si])

def getBestParams(f1Rows, f2Row, f3Rows):
    bestF1 = None
    bestF2 = None
    bestF3 = None
    if f1Rows != None:
        for r in f1Rows:
            topicId = int(row[0])
            feature = row[1]
            colSource = row
    if f2Row != None:
        pass
    if f3Row != None:
        pass


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage:', sys.argv[0], 'resultCSV', file=sys.stderr)
        exit(-1)
    resultCSV = sys.argv[1]

    dataType = ['str', 'str','str', 'str', 'str', 'str', 
            'str', 'str', 'float', 'float', 'float']
    (colNameMap, data) = readCSV(resultCSV, dataType)
    assert len(colNameMap) == len(dataType)
    
    topicList = [2, 3, 4, 5, 6, 13, 16]
    # first framework (self train->self test)
    f1Rows = dict()
    for t in topicList:
        newData = allowData(data, colNameMap, 'topicId', allow='%d' % t, type='string')
        sortByColumn(newData, colNameMap, 'MacroF1', reverse=True)
        f1Rows[t] = newData[0]
    
    # second framework (whole train-> whole test)
    newData = allowData(data, colNameMap, 'experimental settings', allow='allMixed', type='string')
    sortByColumn(newData, colNameMap, 'MacroF1', reverse=True)
    f2Row = newData[0]

    # third framework (leave one test)
    f3Rows = dict()
    for t in topicList:
        newData = allowData(data, colNameMap, 'experimental settings', allow='Test on %d' % t, type='string')
        sortByColumn(newData, colNameMap, 'MacroF1', reverse=True)
        f3Rows[t] = newData[0]

    printResultSummary(topicList, f1Rows, f2Row, f3Rows, colNameMap, 'MacroF1')

