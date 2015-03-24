

def list2Str(L, sep=' '):
    buf = '['
    for i, e in enumerate(L):
        if i == 0:
            buf += e
        else:
            buf += sep + e
        if i == len(L) - 1:
            buf += ']'
    return buf

def dict2Str(D, sep=' '):
    buf = '{'
    for key, value in D.items():
        buf += sep + str(key) + ':' + str(value) 
    buf += '}'
    return buf
        
