import requests
import json
import sys


#TODO: depParse & constParse together

# segment zht string to zht string, " " is the sep
def sendSegmentRequest(sentence):
    api_url = 'http://localhost:8000/segmenter'
    payload = {
        's': sentence        
    }
    r = requests.get(api_url, params = payload)
    if r.status_code == 200:
        return r.text
    else:
        return None

#print(sendSegmentRequest("測試 我是一個句子"))

# typedDependency format:  reln gov_index gov_word gov_tag dep_index dep_word dep_tag
def sendDepParseRequest(sentence, seg=False, draw=False, fileFolder=None, 
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

#print(sendDepParseRequest("我是一個人", draw = True, fileFolder='test'))
#print(sendDepParseRequest("這是一個測試用的句子"))
#print(sendDepParseRequest("台灣應廢除死刑"))	

#s = "I hate this product"
#print(sendDepParseRequest(s, seg=True, draw=True, fileName=s, fileFolder='./'))
#s = "This is a beautiful, useful and cheap product."
#print(sendDepParseRequest(s, seg=True, draw=True, fileName=s, fileFolder='./'))
#s = "This is a beautiful ring in the box."
#print(sendDepParseRequest(s, seg=True, draw=True, fileName=s, fileFolder='./'))


#constituent parsing by stanford pcfg parser
def sendConstParseRequest(sentence, seg=False, returnTokenizedSent=False):
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
        nodeLines = lines[2:2+nodesNum]
        edgeLines = lines[2+nodesNum:]
        '''
        nodes = list()
        edges = list()
        for line in lines[2:2+nodesNum]:
            entry = line.strip().split(' ')
            nodes.append((int(entry[0]), entry[1], entry[2]))
        for line in lines[2+nodesNum:]:
            entry = line.strip().split(' ')
            edges.append((int(entry[0]),int(entry[1])))
        '''
        if returnTokenizedSent:
            return (tokenizedSent, nodeLines, edgeLines)
        else:
            return (nodeLines, edgeLines)
    else:
        return None

#print(sendConstParseRequest("我是一個人", returnTokenizedSent=True))
#print(sendConstParseRequest("這是一個測試用的句子"))
#print(sendConstParseRequest("台灣應廢除死刑"))

def sendTagRequest(sentence, seg=True):
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

#print(sendTagRequest(sendSegmentRequest("我是一個人")))

