
import sys

from RunExperiments import ResultPrinter
from misc import *

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


# merge the rows with the same setting, average the results
# keyPrefixNum: the number of columns to be merged as key
def mergeRows(data, colNameMap, keyPrefixNum):
    keyData = dict()
    #print(len(data[0]))
    for d in data:
        key = tuple(d[0:keyPrefixNum])
        if key not in keyData:
            keyData[key] = list()
        keyData[key].append(d)
    
    newData = list()
    for key, dList in keyData.items():
        #print('key:', key)
        print('num:', len(dList))
        #if len(dList) == 10:
        #    for d in dList:
        #        print(d)
        #    print('')
        #assert len(dList) == 5
        avgD = [0.0 for i in range(0, len(colNameMap) - keyPrefixNum)]
        for d in dList:
            #print(d[keyPrefixNum:len(colNameMap)])
            for i, e in enumerate(d[keyPrefixNum:len(colNameMap)]):
                if type(e) == int or type(e) == float:
                    avgD[i] += e
        for i in range(0, len(colNameMap) - keyPrefixNum):
            avgD[i] /= len(dList)
        #print('Average score:', avgD)
        newRow = list(key)
        newRow.extend(avgD)
        #print(newRow)
        newData.append(newRow)
    return newData

def floatEq(f1, f2):
    return fabs(f1 - f2) < 1e-10

# f1Rows: topic -> a row of self-train to self-test
# f2Row: a row of all-train-all-test
# f3Rows: topic -> a row of leave-one-test
def printResultSummary(topicList, f1Rows, f2Row, f3Rows, colNameMap, scoreName, outfile=sys.stdout):
    print('TopicId, Self-TrainTest(%s), LeaveOneTest(%s), All-TrainTest(%s)' % (scoreName, scoreName, scoreName), file=outfile)
    si = colNameMap[scoreName]
    for t in topicList:
        print('%d, %f, %f, ' % (t, f1Rows[t][si], f3Rows[t][si]), file=outfile)
    print('All,         ,         , %f' % f2Row[si], file=outfile)

def printResultSummary2(topicList, f1Rows, f2Row, f3Rows, colNameMap, scoreName, outfile=sys.stdout):
    si = colNameMap[scoreName]
    print('TopicId', end='', file=outfile)
    for t in topicList:
        print(',', t, end='', file=outfile)
    print('\nSelfTrainTest', end='', file=outfile)
    for t in topicList:
        print(',', f1Rows[t][si], end='', file=outfile)
    print('\nLeaveOneTest', end='',file=outfile)
    for t in topicList:
        print(',', f3Rows[t][si], end='', file=outfile)
    print('\nAllTrainTest', end='',file=outfile)
    print(',', f2Row[si], file=outfile)

def printBestRows(topicList, f1Rows, f2Row, f3Rows, outfile=sys.stdout):
    ResultPrinter.printFirstLine()
    for t in topicList:
        print(f1Rows[t], file=outfile)
    for t in topicList:
        print(f3Rows[t], file=outfile)
    print(f2Row, file=outfile)

# f1TopicRows: topic -> a list of rows
# f2Rows: a list of rows
# f3TopicRows: topic -> a list of rows
def getBestParams(f1TopicRows, f2Rows, f3TopicRows, colNameMap, extractColType):
    f1Params = f2Params = f3Parms = None
    if f1Rows != None:
        f1Params = dict()
        for topicId, rows in f1TopicRows.items():
            f1Params[topicId] = list()
            for r in rows:
                params = getParamFromRow(r, colNameMap, extractColType)
                f1Params[topicId].append(params)

    if f2Row != None:
        f2Params = list()
        for r in f2Rows:
            f2Params.append(getParamFromRow(r, colNameMap, extractColType))

    if f3Rows != None:
        f3Params = dict()
        for topicId, rows in f3TopicRows.items():
            f3Params[topicId] = list()
            for r in rows:
                params = getParamFromRow(r, colNameMap, extractColType)
                f3Params[topicId].append(params)

    return (f1Params, f2Params, f3Params)
    

def getParamFromRow(row, colNameMap, extractColType):
    params = dict()
    for col,type in extractColType.items():
        if type == 'dict' or type == 'list':
            params[col] = str2Var(row[colNameMap[col]])
        elif type == 'bool':
            params[col] = bool(row[colNameMap[col]])
        elif type == 'str':
            params[col] = row[colNameMap[col]]
    return params

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Usage:', sys.argv[0], 'targetScore ResultCSV outParamsFile printBestRow(0/1) [mergeRowKeyPrefixNum]', file=sys.stderr)
        exit(-1)
    targetScore = sys.argv[1]
    resultCSV = sys.argv[2]
    outParamsFile = sys.argv[3]
    printBR = int(sys.argv[4])

    dataType = ResultPrinter.getDataType()
    (colNameMap, data) = readCSV(resultCSV, dataType)
    assert len(colNameMap) == len(dataType)
    
    if len(sys.argv) == 6:
        keyPrefixNum = int(sys.argv[5])
        data = mergeRows(data, colNameMap, keyPrefixNum)
    for d in data:
        print(d)

    topicList = [2, 3, 4, 5, 6, 13, 16]
    firstN = 2
    # find the rows with best score 
    # first framework (self-train-test)
    f1Rows = dict()
    f1TopicRows = dict()
    for t in topicList:
        newData = allowData(data, colNameMap, 'experimental settings', allow=set(['selfTrainTest']), type='string')
        newData = allowData(newData, colNameMap, 'topicId', allow=set(['%d' % t]), type='string')
        #for d in newData:
        #    print(d)
        #print('\n\n')
        sortByColumn(newData, colNameMap, targetScore, reverse=True)
        f1Rows[t] = newData[0]
        f1TopicRows[t] = list()
        for i in range(0, firstN):
            if i < len(newData):
                f1TopicRows[t].append(newData[i])
    
    # second framework (whole train-> whole test)
    newData = allowData(data, colNameMap, 'experimental settings', allow=set(['allMixed']), type='string')
    #for d in newData:
    #    print(d)
    #print('\n\n')
    sortByColumn(newData, colNameMap, targetScore, reverse=True)
    f2Row = newData[0]
    f2Rows = list()
    for i in range(0, firstN):
        if i < len(newData):
            f2Rows.append(newData[i])


    # third framework (leave one test)
    f3Rows = dict()
    f3TopicRows = dict()
    for t in topicList:
        #for d in newData:
        #    print(d)
        #print('\n\n')
        newData = allowData(data, colNameMap, 'experimental settings', allow=set(['Test on %d'% t]), type='string')
        sortByColumn(newData, colNameMap, targetScore, reverse=True)
        f3Rows[t] = newData[0]
        f3TopicRows[t] = list()
        for i in range(0, firstN):
            if i < len(newData):
                f3TopicRows[t].append(newData[i])
    if printBR:
        printBestRows(topicList, f1Rows, f2Row, f3Rows)
    printResultSummary2(topicList, f1Rows, f2Row, f3Rows, colNameMap, targetScore)
    extractColType = { 
        #'feature': 'str', 
        'model settings': 'dict', 
        #'column source': 'list'
        #'statementCol': 'bool'
    }

    if len(sys.argv) < 6:
        print('\n***** Please Note that the results are not averaged ******\n', file=sys.stderr)

    # get best N params of given model
    
    (f1Params, f2Params, f3Params) = getBestParams(f1TopicRows, f2Rows, f3TopicRows, colNameMap, extractColType)
    result = dict()
    result['SelfTrainTest'] = f1Params
    result['AllTrainTest'] = f2Params
    result['LeaveOneTest'] = f3Params

    with open(outParamsFile, 'w') as f:
        json.dump(result, f, indent=2)
    
