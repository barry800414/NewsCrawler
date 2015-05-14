#!/usr/bin/env python3

import sys
import json
import math
from collections import defaultdict

import numpy as np
from scipy.sparse import csr_matrix, csc_matrix, hstack
from sklearn.grid_search import ParameterGrid

from RunExperiments import *
from misc import *
from Volc import Volc

'''
This is the improved version of WordModel
 1.remove < 1 dimension (DONE)
 2.allowed some of pos taggers (DONE)
 3.word clustering 
 4.highest tfidf

Author: Wei-Ming Chen
Date: 2015/05/04

'''


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
    if len(sys.argv) != 2:
        print('Usage:', sys.argv[0], 'labelNewsJson', file=sys.stderr)
        exit(-1)
    
    # arguments
    labelNewsJson = sys.argv[1]

    # load labels and news 
    with open(labelNewsJson, 'r') as f:
        labelNewsList = json.load(f)
    
    labelNewsInTopic = divideLabel(labelNewsList)

    # SelfTrainTest
    
    
    # AllTrainTest
    # LeaveOneTest
    

    
