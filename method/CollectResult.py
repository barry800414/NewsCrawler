
import sys

import numpy as np
from RunExperiments import ResultPrinter
from misc import *
from ConfidenceInterval import *


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
                    elif dataType[i] == 'dict':
                        row.append(str2Var(e))
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
def mergeRows(data, colNameMap, keyPrefixNum, dataType):
    keyData = dict()
    # grouping data with same key
    for d in data:
        key = tuple(d[0:keyPrefixNum])
        if key not in keyData:
            keyData[key] = list()
        keyData[key].append(d)
    
    # calculate mean, stdev, confidence interval for columns
    newData = list()
    for key, dList in keyData.items():
        #print('key:', key)
        #print(len(dList), end=',')
        #if len(dList) == 10:
        #    for d in dList:
        #        print(d)
        #    print('')
        newRow = list(key)
        for i in range(0, len(colNameMap) - keyPrefixNum):
            if dataType[i + keyPrefixNum] in ['int', 'float']:
                data = [d[i + keyPrefixNum] for d in dList]
                mean = np.mean(data)
                stdev = np.std(data, ddof=1)
                interval = calcConfidenceInterval(mean, stdev, len(data))
                newRow.extend([mean, stdev, interval])
            elif dataType[i + keyPrefixNum] in ['dict']:
                keyList = sorted(dList[0][i + keyPrefixNum].keys())
                for key in keyList:
                    data = [d[i + keyPrefixNum][key] for d in dList]
                    mean = np.mean(data)
                    stdev = np.std(data, ddof=1)
                    interval = calcConfidenceInterval(mean, stdev, len(data))
                    newRow.extend([mean, stdev, interval])
            else:
                newRow.append(None)
        newData.append(newRow)
    
    # update colNameMap
    inverseMap = [name for name,i in sorted(colNameMap.items(), key=lambda x:x[1])]
    newMap = dict()
    nowIndex = 0
    for i in range(0, len(colNameMap)):
        if i < keyPrefixNum:
            newMap[inverseMap[i]] = nowIndex
            nowIndex += 1
        else:
            if dataType[i] in ['int', 'float']:
                newMap[inverseMap[i]] = nowIndex
                newMap[inverseMap[i] + '_stdev'] = nowIndex + 1
                newMap[inverseMap[i] + '_interval'] = nowIndex + 2
                nowIndex = nowIndex + 3
            elif dataType[i] in ['dict']:
                keyList = sorted(dList[0][i].keys())
                for key in keyList:
                    newMap[key] = nowIndex
                    newMap[key + '_stdev'] = nowIndex + 1
                    newMap[key + '_interval'] = nowIndex + 2
                    nowIndex = nowIndex + 3
            else:
                newMap[inverseMap[i]] = nowIndex
                nowIndex += 1

    #for name, index in sorted(colNameMap.items(), key=lambda x:x[1]):
    #    print(name, index)
    #for name, index in sorted(newMap.items(), key=lambda x:x[1]):
    #    print(name, index)
    #print(len(newData[0]))

    return (newData, newMap)

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

def printResultSummary2(topicList, f1Rows, f2Row, f3Rows, colNameMap, scoreName, framework, methodName, outfile=sys.stdout):
    si = colNameMap[scoreName]
    #print('TopicId', end='', file=outfile)
    #for t in topicList:
    #    print(',', t, end='', file=outfile)
    
    if framework == 'SelfTrainTest':
        print(methodName, 'SelfTrainTest', sep=',', end='', file=outfile)
        for t in topicList:
            iname = scoreName + '_interval' 
            if iname in colNameMap:
                print(',%f,%f' % (f1Rows[t][si], f1Rows[t][colNameMap[iname]]), end='', file=outfile)
            else:
                print(',', f1Rows[t][si], end='', file=outfile)
        print('',file=outfile)
    elif framework == 'LeaveOneTest':
        print(methodName, 'LeaveOneTest', sep=',', end='',file=outfile)
        for t in topicList:
            iname = scoreName + '_interval' 
            if iname in colNameMap:
                print(',%f,%f' % (f3Rows[t][si], f3Rows[t][colNameMap[iname]]), end='', file=outfile)
            else:
                print(',', f3Rows[t][si], end='', file=outfile)
        print('', file=outfile)
    elif framework == 'AllTrainTest':
        print(methodName, 'AllTrainTest',sep=',', end='',file=outfile)
        iname = scoreName + '_interval' 
        if iname in colNameMap:
            print(',%f,%f' % (f2Row[si], f2Row[colNameMap[iname]]), file=outfile)
        else:
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
        print('Usage:', sys.argv[0], 'targetScore framework methodName ResultCSV printBestRow(0/1) [mergeRowKeyPrefixNum]', file=sys.stderr)
        exit(-1)
    targetScore = sys.argv[1]
    framework = sys.argv[2]
    methodName = sys.argv[3]
    resultCSV = sys.argv[4]
    #outParamsFile = sys.argv[4]
    printBR = int(sys.argv[5])

    dataType = ResultPrinter.getDataType()
    (colNameMap, data) = readCSV(resultCSV, dataType)
    assert len(colNameMap) == len(dataType)
    
    if len(sys.argv) == 7:
        keyPrefixNum = int(sys.argv[6])
        (data, colNameMap) = mergeRows(data, colNameMap, keyPrefixNum, dataType)

    #for d in data:
    #    print(d)

    #topicList = [2, 3, 4, 5, 6, 13, 16]
    topicList = [2, 3, 4, 5, 13]
    #topicList = [4]
    firstN = 1
    # find the rows with best score 
    # first framework (self-train-test)
    f1Rows = dict()
    f1TopicRows = dict()
    if framework == 'SelfTrainTest':
        for t in topicList:
            newData = allowData(data, colNameMap, 'experimental settings', allow=set(['selfTrainTest']), type='string')
            newData = allowData(newData, colNameMap, 'topicId', allow=set(['%d' % t]), type='string')
            #assert len(newData) == 1
            f1Rows[t] = newData[0]
    
    # second framework (whole train-> whole test)
    f2Row = None
    if framework == 'AllTrainTest':
        newData = allowData(data, colNameMap, 'experimental settings', allow=set(['allMixed']), type='string')
        #assert len(newData) == 1
        f2Row = newData[0]

    # third framework (leave one test)
    f3Rows = dict()
    f3TopicRows = dict()
    if framework == 'LeaveOneTest':
        for t in topicList:
            newData = allowData(data, colNameMap, 'experimental settings', allow=set(['Test on %d'% t]), type='string')
            #assert len(newData) == 1
            f3Rows[t] = newData[0]

    printResultSummary2(topicList, f1Rows, f2Row, f3Rows, colNameMap, targetScore, framework, methodName)

    if len(sys.argv) < 7:
        print('\n***** Please Note that the results are not averaged ******\n', file=sys.stderr)

