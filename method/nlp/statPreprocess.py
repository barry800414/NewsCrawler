#!/usr/bin/env python3
import sys
import json
import re
import random
from NLPToolRequests import *
from parseNews import parseText
from segNews import segText
from tagNews import tagText

# default sentence separator
#SEP = '[;\t\n。；　「」﹝﹞【】《》〈〉（）〔〕『 』\(\)\[\]!?？！]'

SEP = '[,;\t\n，。；　「」﹝﹞【】《》〈〉（）〔〕『 』\(\)\[\]!?？！]'

# default new sentence separator
NEW_SEP = ','

# default to-removed punctuation
TO_REMOVE = '[\uF0D8\u0095/=&�+:：／\|‧]'
#TO_REMOVE = '[\uF0D8\u0095/=&�+、:：／\|‧]'

# default brackets for fixing them (not to segment)
BRACKETS = [ ('[', ']'), ('(', ')'), ('{', '}'), 
             ('〈', '〉'), ('《', '》'), ('【', '】'),
             ('﹝', '﹞'), ('「','」'), ('『', '』'), 
             ('（','）'), ('〔','〕')]

allRelationSet = set()

def preStat(statDict):
    for statId, statObj in statDict.items():
        stat = statObj['original']
        statObj['seg'] = segText(stat)
        statObj['pos'] = tagText(stat)
        statObj['dep'] = parseText(stat)
    return statDict

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'InStatJson OutStatJson', file=sys.stderr)
        exit(-1)
    inStatJsonFile = sys.argv[1]
    outStatJsonFile = sys.argv[2]
    with open(inStatJsonFile, 'r') as f:
        statDict = json.load(f)
    
    statDict = preStat(statDict)

    with open(outStatJsonFile, 'w') as f:
        json.dump(statDict, f, ensure_ascii=False, indent = 2)


