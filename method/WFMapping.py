
import json

'''
This code implements the function for
reading word-frequency mapping from files
'''

WF_Folder = './'

# load word-frequency mapping for each statement
def loadWFDict(filename):
    with open(filename, 'r') as f:
        WFDict = json.load(f)
        # convert string to integer
        newDict = dict()
        for key, value in WFDict.items():
            newDict[int(key)] = value
    return newDict

def addToWFDict(wfTo, wfFrom):
    for key, value in wfFrom.items():
        if key in wfTo:
            wfTo[key] += value
        else:
            wfTo[key] = value

# deprecated
# allowedType : the list of allowed POS-tagger types
def mergeWFDict(allowedType):
    WFDict = dict()
    for type in allowedType:
        tmpDict = loadWFDict(WF_Folder + '%s_List.json' % (type))
        addToWFDict(WFDict, tmpDict)
    return WFDict

# filter the words in word-frequency dict, return a set of allowed words
def filteredByThreshold(wf, threshold):
    words = set()
    fSum = sum(wf.values())
    for w, f in wf.items():
        if float(f)/fSum >= threshold:
            words.add(w)
    return words

# get allowed words for each type of POS tagger,
# return a dict (pos-tagger -> set of allowed words)
# WFDictInTopic[P]: the word-frequency mapping of POS-tag P
def getAllowedWords(WFDictInTopic, allowedPOSType, threshold):
    allowedWords = dict()
    for pos in allowedPOSType:
        allowedWords[pos] = filteredByThreshold(WFDictInTopic[pos], threshold)
    return allowedWords
