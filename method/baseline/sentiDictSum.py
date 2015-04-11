#!/usr/bin/env python3

import sys
import json
import dataPreprocess

# return a dict (word -> sentiment score)
def readSentiDict(filename):
    sentiDict = dict()
    dupSet = set()
    with open(filename, 'r') as f:
        for i, line in enumerate(f):
            entry = line.strip().split(',')
            if len(entry) != 2:
                print('Line %d format error:' %(i+1), entry, file=sys.stderr)
                continue
            w = entry[0]
            s = int(entry[1])
            if w in sentiDict:
                #print(w, 'is already in dictionary', file=sys.stderr)
                dupSet.add(w)
            else:
                sentiDict[w] = s

    for w in dupSet:
        del sentiDict[w]
    print(len(dupSet), 'words are +1&-1', file=sys.stderr)
    return sentiDict
		
def sentiDictSumPredict(content, sentiDict):
	sentValue = 0
	for w, sent in sentiDict.items():
		sentValue += content.count(w) * sent

	if sentValue > 0:
		predict = 1
	elif sentValue == 0:
		predict = 0
	else:
		predict = -1

	return predict

def convertToLabel(labelStr):
	if labelStr == 'neutral':
		return 0
	elif labelStr == 'agree':
		return 1
	elif labelStr == 'oppose':
		return -1
	else:
		print('Label string cannot be identified', file=sys.stderr)
		return None

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print('Usage:', sys.argv[0], 'newsJson sentiDict', file=sys.stderr)
		exit(-1)

	newsJsonFile = sys.argv[1]
	sentiDictFile = sys.argv[2]

	with open(newsJsonFile, 'r') as f:
		news = json.load(f)
	news = dataPreprocess.data_cleaning(news)

	dataPreprocess.printStatInfo(news)
	
	sentiDict = readSentiDict(sentiDictFile)

	accu = 0
	labelTypeNum = [0, 0, 0]
	newsCnt = 0
	for n in news:
		label = convertToLabel(n['label'])
		if label == None:
			continue
		newsCnt += 1
		labelTypeNum[label+1] += 1
		predict = sentiDictSumPredict(n['news']['content'], sentiDict)
		if label == predict:
			accu += 1
		print('Label:', label, ' Predict:', predict)

	print('Accuracy: %f(%d/%d)' % (float(accu)/newsCnt, accu, newsCnt))
	print('#agree: %d(%f)  #neutral: %d(%f)  #oppose: %d(%f)' % (labelTypeNum[2], 
		float(labelTypeNum[2])/newsCnt, labelTypeNum[1], float(labelTypeNum[1])/newsCnt,
		labelTypeNum[0], float(labelTypeNum[0])/newsCnt))	
		
