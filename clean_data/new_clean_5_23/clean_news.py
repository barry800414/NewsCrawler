import json
import re

delete_list = [u'立即下載風傳媒APP，世界脈動在你手中！',u'NOWnews 今日新聞網',u'※',u'延伸閱讀：','<feff>','延伸閱讀',u'敬請刊登',u'聯絡電話：',u'電子郵件信箱：',u'本新聞稿發言人：',u'貿易局承辦單位聯絡人：',u'【與自由共舞 線上看】',u'【',u'】',u'【深入獨立特派員】','()',u'聯合晚報@',u'<95>',u'相關影音：',u'圖片版權billy1125CC License',u'圖片版權']
re_list = [r"(http|ftp|https|httpv):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+    #])?",r"\d{7,10}",r"/^[a-z]([a-z0-9]*[-_]?[a-z0-9]+)*@([a-z0-9]*[-_]?[a-z0-9]+)+[\.][a-z]{2,3}([\.][a-z]{2})?$/i",r"^[0-9]{4}-(((0[13578]|(10|12))-(0[1-9]|[1-2][0-9]|3[0-1]))|(02-(0[1-9]|[1-2][0-9]))|((0[469]|11)-(0[1-9]|[1-2][0-9]|30)))$",r"(?=\d)^(?:(?!(?:10\D(?:0?[5-9]|1[0-4])\D(?:1582))|(?:0?9\D(?:0?[3-9]|1[0-3])\D(?:1752)))((?:0?[13578]|1[02])|(?:0?[469]|11)(?!\/31)(?!-31)(?!\.31)|(?:0?2(?=.?(?:(?:29.(?!000[04]|(?:(?:1[^0-6]|[2468][^048]|[3579][^26])00))(?:(?:(?:\d\d)(?:[02468][048]|[13579][26])(?!\x20BC))|(?:00(?:42|3[0369]|2[147]|1[258]|09)\x20BC))))))|(?:0?2(?=.(?:(?:\d\D)|(?:[01]\d)|(?:2[0-8])))))([-.\/])(0?[1-9]|[12]\d|3[01])\2(?!0000)((?=(?:00(?:4[0-5]|[0-3]?\d)\x20BC)|(?:\d{4}(?!\x20BC)))\d{4}(?:\x20BC)?)(?:$|(?=\x20\d)\x20))?((?:(?:0?[1-9]|1[012])(?::[0-5]\d){0,2}(?:\x20[aApP][mM]))|(?:[01]\d|2[0-3])(?::[0-5]\d){1,2})?$"]
print (delete_list)
def load_article():
    #f1 = open('new.json','r')
    f1 = open('toCleanNews_all_in_topic_news.json','r')
    content = json.load(f1)
    for statId,statObj in content.items():
        for re_item in re_list:
            #print (re_item)
            k = re.compile(re_item)
            new_content = k.sub('',statObj['content'])
            #print (new_content)
            #print (statObj['content'])
            #input()
            statObj['content'] = new_content
        for dell_item in delete_list:
            if statObj['content'].find(dell_item) != -1:
                new_content =  (statObj['content'].replace(dell_item,u''))
                statObj['content'] = new_content
    f1.close()
    with open('new_clean.json','w') as fw:
        json.dump(content,fw,ensure_ascii=False,indent=2)
def main():
    load_article()

if __name__ == "__main__":
    main()
