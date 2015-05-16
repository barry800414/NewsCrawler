#!/usr/bin/env python3

import sys
import json
import random

import numpy as np
from RunRandomExp import *

def getLabels(labelNewsList):
    mapping = { "neutral" : 1, "oppose": 0, "agree" : 2 } 
    labelList = list()
    for labelNews in labelNewsList:
        if labelNews['label'] in mapping:
            labelList.append(mapping[labelNews['label']])
    return labelList

def divideLabel(labelNewsList):
    #FIXME stat and topic
    labelNewsInTopic = dict()
    for labelNews in labelNewsList:
        statId = labelNews['statement_id']
        if statId not in labelNewsInTopic:
            labelNewsInTopic[statId] = list()
        labelNewsInTopic[statId].append(labelNews)
    return labelNewsInTopic

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'labelNewsJson trialNum', file=sys.stderr)
        exit(-1)
    
    # arguments
    labelNewsJson = sys.argv[1]
    trialNum = int(sys.argv[2])

    # load labels and news 
    with open(labelNewsJson, 'r') as f:
        labelNewsList = json.load(f)

    labelNewsInTopic = divideLabel(labelNewsList)

    # SelfTrainTest
    print('SelfTrainTest ...')
    for topicId, ln in sorted(labelNewsInTopic.items(), key=lambda x:x[0]):
        y = np.array(getLabels(ln))
        avg = 0.0
        for i in range(0, trialNum):
            r = RunExp.selfTrainTest(y, 'MacroF1', testSize=0.2, randSeed=i)
            avg += r['MacroF1']
            if (i+1) % 10 == 0:
                print('%c%d/%d' % (13, i+1, trialNum), end='')
        avg /= trialNum
        print('%cTopic %d, %f' % (13, topicId, avg))

    # AllTrainTest
    print('AllTrainTest ...')
    y = np.array(getLabels(labelNewsList))
    topicMap = [ labelNewsList[i]['statement_id'] for i in range(0, len(labelNewsList)) ]

    avg = 0.0
    for i in range(0, trialNum):
        r = RunExp.allTrainTest(y, topicMap, "MacroF1", testSize=0.2, randSeed=i)
        avg += r['MacroF1']
        if (i+1) % 10 == 0:
            print('%c%d/%d' % (13, i+1, trialNum), end='')

    avg /= trialNum
    print('%cAll, %f' % (13,avg))

    # LeaveOneTest
    print('LeaveOneTest ...')
    for topicId in sorted(labelNewsInTopic.keys()):
        avg = 0.0
        for i in range(0, trialNum):
            r = RunExp.leaveOneTest(y, topicMap, "MacroF1", randSeed=i, testTopic=topicId)
            avg += r['MacroF1']
            if (i+1) % 10 == 0:
                print('%c%d/%d' % (13, i+1, trialNum), end='')

        avg /= trialNum
        print('%cTopic %d, %f' % (13, topicId, avg))


    
