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
def parseStr(sentence, draw=False, fileFolder=None, fileName=None, returnTokenizedSent=False):
    #api_url = 'http://localhost:8000/nn_dep'
    api_url = 'http://localhost:8000/pcfg_dep'
    payload = {
        's': sentence        
    }
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

#print(parseStr("我是一個人", draw = True, fileFolder='test'))
#print(parseStr("這是一個測試用的句子"))
#print(parseStr("台灣應廢除死刑"))


def tagStr(sentence):
    api_url = 'http://localhost:8000/pos'
    payload = {
        's': sentence        
    }
    r = requests.get(api_url, params = payload)
    if r.status_code == 200:
        return r.text
    else:
        return None

#print(tagStr(segmentStr("我是一個人")))

