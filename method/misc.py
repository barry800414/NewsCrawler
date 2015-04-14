
import json

def toStr(v, sep='**'):
    outStr = json.dumps(v)
    outStr = outStr.replace(',', sep)
    return outStr

def str2Var(inStr, sep='**'):
    return json.loads(inStr.replace(sep, ','))


def toFStr(v):
    outStr = json.dumps(v)
    outStr = outStr.replace("'", '')
    outStr = outStr.replace('"', '')
    outStr = outStr.replace(',', '')
    outStr = outStr.replace(' ', '')
    return outStr

