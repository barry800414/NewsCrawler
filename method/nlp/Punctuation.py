
import json
import sys
import re

# reserved words in regular expression
reservedSet = set(['[', ']', '\\', '.', '^', '$', '*', '+', '?', '|', '(', ')', '-'])

def readJsonFile(filename):
    with open(filename, 'r') as f:
        p = json.load(f)
    return p

# d: dictionary (word->hex string)
def toRegexStr(d):
    pSet = set(d.keys())
    rStr = '['
    for p in pSet:
        if p in reservedSet:
            rStr += '\\' + p
        else:
            rStr += p
    rStr += ']'
    return rStr

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage:', sys.argv[0], 'punctuationJson', file=sys.stderr)
        exit(-1)

    p = readJsonFile(sys.argv[1])
    rStr = toRegexStr(p['sep'])
    print('Regular Expression:', rStr)
    testStr = '1.2,3 4\t5\n6'
    print('TestStr:', testStr)
    print('After substitution:', re.sub(rStr, ' ', testStr), '|||')

    rStr = toRegexStr(p['remove'])
    print('Regular Expression:', rStr)
    testStr = '1.2,3 4\t5\n6～'
    print('TestStr:', testStr)
    print('After substitution:', re.sub(rStr, ' ', testStr), '|||')


