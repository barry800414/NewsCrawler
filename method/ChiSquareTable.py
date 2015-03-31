#!/usr/bin/env python3 

import sys
import math
from operator import itemgetter

'''
This module is to provide ChiSquareTable class
'''

class ChiSquareTable:
    INF=99999999999.0

    # classNum: #possible class
    # itemNum: #possible item
    # classDocCnt[j]: number of doc with class j
    # classItemCnt[i][j] number of doc with item i and class j
    def calcTable(classNum, itemNum, classDocCnt, classItemCnt):
        return [[ChiSquareTable.calcValue(i, c, classDocCnt, classItemCnt) for i in range(0, itemNum)] for c in range(0, classNum)]

    # i: index of item, c: index of class
    def calcValue(i, c, classDocCnt, classItemCnt):
        A = classItemCnt[i][c]
        B = classDocCnt[c] - A
        C = sum(classItemCnt[i]) - A
        D = (sum(classDocCnt) - classDocCnt[c]) - C
        N = A + B + C + D
        deno = ((A+C) * (B+D) * (A+B) * (C+D))
        if deno < 0:
            print(deno, file=sys.stderr)
            print(A, B, C, D, file=sys.stderr)
        if deno == 0:
            return ChiSquareTable.INF
        else:
            value = (N * math.pow((A*D - C*B), 2.0)) / deno
            return value 
    
    def print(chiTable, classMap, itemMap, outfile=sys.stdout, printValue=False):
        for i, chiList in enumerate(chiTable):
            c = classMap[i]
            print('Class %s' % (c), end=':', file=outfile)
            sortedList = sorted(enumerate(chiList), key=itemgetter(1), reverse=True)
            for itemIndex, value in sortedList:
                print(' %s' % (itemMap[itemIndex]), end='', file=outfile)
                if printValue:
                    print(';%.2f' % (value), end=' ', file=outfile)
            print('',file=outfile)
