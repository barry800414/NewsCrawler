
import json
import sys
from collections import defaultdict
from misc import *

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'taggedLabelNewsJsonFile outFilePrefix', file=sys.stderr)
        exit(-1)

    with open(sys.argv[1], 'r') as f:
        labelNewsList = json.load(f)


    labelNewsInTopic = divideLabelNewsByTopic(labelNewsList)
    allowedPOS=["VA", "VV", "NN", "NR", "AD", "JJ"]

    # for each topic
    for topicId, lns in labelNewsInTopic.items():
        wordCnt = defaultdict(int)
        for labelNews in lns:
            content = labelNews['news']['content_pos']
            for sent in content.split(','):
                for wt in sent.split(' '):
                    (w, t) = wt.split('/')
                    if t in allowedPOS:
                        wordCnt[w] += 1
        printWordCnt(wordCnt, sys.argv[2] + '_T%d_W.txt' % topicId)


    # all
    wordCnt = defaultdict(int)
    for labelNews in labelNewsList:
        content = labelNews['news']['content_pos']
        for sent in content.split(','):
            for wt in sent.split(' '):
                (w, t) = wt.split('/')
                if t in allowedPOS:
                    wordCnt[w] += 1
    printWordCnt(wordCnt, sys.argv[2] + '_TAll_W.txt')
    

