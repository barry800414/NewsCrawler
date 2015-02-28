#!/usr/bin/env python3

import sys
import json

# return a dict (word -> sentiment score)
def readSentDict(filename):
	sentDict = dict()
	with open(filename, 'r') as f:
		for line in f:
			entry = line.strip().split(',')
			if len(entry) != 2:
				print('This line format error:', entry, file=sys.stderr)
				continue
			
			w = entry[0]
			s = int(entry[1])
			sentDict[w] = s
	return sentDict
		
def sentDictSumPredict(content, sentDict):
	sentValue = 0
	for w, sent in sentDict.items():
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
		print('Usage:', sys.argv[0], 'newsJson sentDict', file=sys.stderr)
		exit(-1)

	newsJsonFile = sys.argv[1]
	sentDictFile = sys.argv[2]

	with open(newsJsonFile, 'r') as f:
		news = json.load(f)

	sentDict = readSentDict(sentDictFile)

	accu = 0
	labelTypeNum = [0, 0, 0]
	newsCnt = 0
	for n in news:
		label = convertToLabel(n['label'])
		if label == None:
			continue
		newsCnt += 1
		labelTypeNum[label+1] += 1
		predict = sentDictSumPredict(n['news']['content'], sentDict)
		if label == predict:
			accu += 1
		print('Label:', label, ' Predict:', predict)

	print('Accuracy: %f(%d/%d)' % (float(accu)/newsCnt, accu, newsCnt))
	print('#agree: %d(%f)  #neutral: %d(%f)  #oppose: %d(%f)' % (labelTypeNum[2], 
		float(labelTypeNum[2])/newsCnt, labelTypeNum[1], float(labelTypeNum[1])/newsCnt,
		labelTypeNum[0], float(labelTypeNum[0])/newsCnt))	
		
