import sys

def data_cleaning(labelNewsList, printInfo=False):
    labelSet = set(["neutral", "oppose", "agree"])
    #labelSet = set(["neutral", "oppose", "agree"])
    newList = list()
    for labelNews in labelNewsList:
        if labelNews['label'] in labelSet:
            newList.append(labelNews)
    return newList

def printStatInfo(labelNewsList):
    statSet = set() # total possible of statement_id
    stat = dict()
    for labelNews in labelNewsList:
        statSet.add(labelNews['statement_id'])
        stat[labelNews['statement_id']] = labelNews['statement']

    num = dict() # calculate each number for each statement
    for statId in statSet:
        num[statId] = { "agree": 0, "oppose": 0, "neutral": 0 }
    
    for labelNews in labelNewsList:
        num[labelNews['statement_id']][labelNews['label']] += 1

    agreeSum = 0
    neutralSum = 0
    opposeSum = 0
    print('statement ID, statement, agree, neutral, oppose, total',file=sys.stderr)
    for statId in statSet:
        agree = num[statId]['agree']
        neutral = num[statId]['neutral']
        oppose = num[statId]['oppose']
        total = agree + neutral + oppose
        print('%d, %s, %d(%.1f%%), %d(%.1f%%), %d(%.1f%%), %d' % (statId, stat[statId], 
            agree, 100*float(agree)/total, neutral, 100*float(neutral)/total, 
            oppose, 100*float(oppose)/total, total), file=sys.stderr)
        agreeSum += agree
        neutralSum += neutral
        opposeSum += oppose
    totalSum = agreeSum + neutralSum + opposeSum
    print('Total, , %d(%.1f%%), %d(%.1f%%), %d(%.1f%%), %d' % (agreeSum, 
        100*float(agreeSum)/totalSum, neutralSum, 
        100*float(neutralSum)/totalSum, opposeSum, 
        100*float(opposeSum)/totalSum, totalSum), file=sys.stderr)

# merge news file, label file, and statement file to one object
def mergeToLabelNews(newsDict, labelList, statDict, newsCol=["content","title"], statCol):
    newList = list()
    for labelDict in labelList:
        newDict = dict(labelDict)
        statId = labelDict['statement_id']
        newsId = labelDict['news_id']
        if statId in statDict:
            sDict = dict()
            for c in statCol:
                sDict[c] = statDict[statId][c]
            newDict['statement'] = sDict
        else:
            print('%d not found in statement list' % statId, file=sys.stderr)
        if newsId in newsDict:
            nDict = dict()
            for c in newsCol:
                nDict[c] = newsDict[newsId][c]
            newsDict['news'] = nDict
        else:
            print('%s not found in news corpus' % newsId, file=sys.stderr)
        newList.append(newDict)

    return newList





if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage:', sys.argv[0], 'labelNewsJson', file=sys.stderr)
        exit(-1)

    
