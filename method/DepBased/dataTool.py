

def divideNewsByTopic(newsDict):
    topicNews = dict()
    for newsId, news in newsDict.items():
        topics = news['topic']
        for t in topics:
            if t not in topicNews:
                topicNews[t] = dict()
            topicNews[t][newsId] = news
    return topicNews


def divideLabel(labelNewsList):
    #FIXME stat and topic
    labelNewsInTopic = dict()
    for labelNews in labelNewsList:
        statId = labelNews['statement_id']
        if statId not in labelNewsInTopic:
            labelNewsInTopic[statId] = list()
        labelNewsInTopic[statId].append(labelNews)
    return labelNewsInTopic


