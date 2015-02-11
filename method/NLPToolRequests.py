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

segmentStr("測試 《我是一個句子》")

def parseStr(sentence):
    api_url = 'http://localhost:8000/dep_parser'
    payload = {
        's': sentence        
    }
    r = requests.get(api_url, params = payload)
    if r.status_code == 200:
        return r.text
    else:
        return None

parseStr("我是一個人")

