import requests
import json
import sys

payload={
    's': u'簽訂服務貿易協定', 
}

# segment zht string to zht string, " " is the sep
def segmentStr(sentence):
    api_url = 'http://localhost:8000/segmenter'
    payload = {
        's': sentence        
    }
    r = requests.get(api_url, params = payload)
    #print(r.url)
    if r.status_code == 200:
        return r.text
    else:
        return None

#print(segmentStr("測試 我是一個句子"))

# typedDependency format:  reln gov_index gov_word gov_tag dep_index dep_word dep_tag
def depParseStr(sentence, seg=False, draw=False, fileFolder=None, 
        fileName=None, returnTokenizedSent=False):
    api_url = 'http://localhost:8000/pcfg_dep'
    
    if seg == False:
        payload = { 's': sentence }
    else:
        payload = { 'seg_s': sentence }

    if draw == True and fileFolder != None and fileName != None:
        payload['f_folder'] = fileFolder
        payload['f_name'] = fileName
        payload['draw'] = True
        
    r = requests.get(api_url, params = payload)
    if r.status_code == 200:
        lines = r.text.strip().split('\n')
        tokenizedSent = lines[0]
        typedDependencies = lines[1:]
        if returnTokenizedSent:
            return (tokenizedSent, typedDependencies)
        else:
            return typedDependencies
    else:
        return None

#print(depParseStr("我是一個人", draw = True, fileFolder='test'))
#print(depParseStr("這是一個測試用的句子"))
#print(depParseStr("台灣應廢除死刑"))		
		
		
#constituent parsing by stanford pcfg parser
def constParseStr(sentence, seg=False, returnTokenizedSent=False):
    api_url = 'http://localhost:8000/pcfg'
    
    if seg == False:
        payload = { 's': sentence }
    else:
        payload = { 'seg_s': sentence }
        
    r = requests.get(api_url, params = payload)
    if r.status_code == 200:
        lines = r.text.strip().split('\n')
        tokenizedSent = lines[0]
        entry = lines[1].strip().split(' ')
        nodesNum = int(entry[0])
        edgesNum = int(entry[1])
        assert (nodesNum + edgesNum + 2) == len(lines)
        nodes = list()
        edges = list()
        for line in lines[2:2:nodesNum]:
            entry = line.strip().split(' ')
            nodes.append((int(entry[0]), entry[1], entry[2]))
        for line in lines[2+nodesNum:]:
            entry = line.strip().split(' ')
            edges.append((int(entry[0]),int(entrt[1])))
        if returnTokenizedSent:
            return (tokenizedSent, nodes, edges)
        else:
            return (nodes, edges)
    else:
        return None

print(constParseStr("我是一個人"))
#print(constParseStr("這是一個測試用的句子"))
#print(constParseStr("台灣應廢除死刑"))

def tagStr(sentence, seg=True):
    api_url = 'http://localhost:8000/pos'
    if seg == False:
        payload = { 's': sentence }
    else:
        payload = { 'seg_s': sentence }

    r = requests.get(api_url, params = payload)
    if r.status_code == 200:
        return r.text
    else:
        return None

#print(tagStr(segmentStr("我是一個人")))

