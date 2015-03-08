
import json

'''
This code implements the function for
reading word-frequency mapping from files
'''

WF_Folder = './'

# load word-frequency mapping for each statement
def loadWFDict(filename):
    with open(filename, 'r') as f:
        wf = json.load(f)
    return wf

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
def filteredByThreshold(WFDict, threshold):
    words = set()
    fSum = sum(WFDict.values())
    for w, f in WFDict.items():
        if float(f)/fSum >= threshold:
            words.add(w)
    return words

# get allowed words for each type of POS tagger,
# return a dict (pos-tagger -> set of allowed words)
def getAllowedWords(allowedPOSType, threshold, WFDictDict):
    allowedWords = dict()
    for type in allowedPOSType:
        allowedWords[type] = filterByThreshold(WFDictDict[type], threshold)
    return allowedWords
