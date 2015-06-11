
import sys
import json
from collections import defaultdict
from misc import *
from ExtractPhrases import *

# type: the information type of news (POS tags/ constituent parsing)
def countEntityFromTag(taggedNews, entityCnt, allowedPOS=None):
    if allowedPOS == None:
        allowedPOS = set(['NR'])
    content = taggedNews['content_pos']
    for sent in content.split(','):
        for wt in sent.split(' '):
            (w, t) = wt.split('/')
            if t in allowedPOS:
                entityCnt[w] += 1
    return entityCnt

def printPhraseList(pList, filename):
    pList = sorted(pList, key = lambda x:x.cnt, reverse=True)
    with open(filename, 'w') as f:
        for p in pList:
            print(p.getSepStr(), p.cnt, sep=':', file=f)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'labelNewsJsonFile(tagged/const) tag/const', file=sys.stderr)
        exit(-1)

    labelNewsJsonFile = sys.argv[1]
    type = sys.argv[2]
    assert type in ['tag', 'const']
    
    with open(labelNewsJsonFile, 'r') as f:
        labelNewsList = json.load(f)

    labelNewsInTopic = divideLabelNewsByTopic(labelNewsList)

    # for each topic
    for topicId, lns in sorted(labelNewsInTopic.items(), key=lambda x:x[0]):
        if type == 'tag':
            entityCnt = defaultdict(int)
            for labelNews in lns:
                countEntityFromTag(labelNews['news'], entityCnt, allowedPOS=['NN', 'NR'])
            printWordCnt(entityCnt,'entity_%s_topic%d.txt' % (type, topicId), printCnt=True)

        elif type == 'const':
            pList = extractPhrasesFromLabelNewsList(lns, allowedTag=['NP'])
            printPhraseList(pList, 'entity_%s_topic%d.txt' % (type, topicId))
