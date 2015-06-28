
import sys
# This class represent an opinion, which consists of 
# holder, opinion and target(but some of them can be
# None)
# O: opinion
# H: holder
# T: target
# N: negation (to opinion)
class Opinion():
    def __init__(self, pTreeName, opinion=None, holder=None, target=None, negCnt=0, 
            usingOpnTag=False, volcDict=None):
        self.pTreeName = pTreeName
        # original word
        self.opnW = opinion 
        self.hdW = holder
        self.tgW = target
        # word(if no sentiDict) or index(with sentiDict)
        self.opn = opinion
        self.hd = holder
        self.tg = target
        self.usingOpnTag = usingOpnTag
        self.negCnt = negCnt
        self.sign = 1 if negCnt % 2 == 0 else -1
        self.volcDict = volcDict
        self.__convertUsingVolcDict__()

    def genOpnFromDict(d, volcDict, pTreeName):
        opn = d['opinion'] if 'opinion' in d else None
        hd = d['holder'] if 'holder' in d else None
        tg = d['target'] if 'target' in d else None
        # return None if word not in volcabulary
        #if (opn is not None) and (volcDict['opinion'] is not None) and (opn not in volcDict['opinion']):
        #    return None
        #if (hd is not None) and (volcDict['holder'] is not None) and (hd not in volcDict['holder']):
        #    return None
        #if (tg is not None) and (volcDict['target'] is not None) and (tg not in volcDict['target']):
        #    return None
        negCnt = d['neg']['opinion'] if 'neg' in d and 'opinion' in d['neg'] else 0
        opn = d['opinion_tag'] if 'opinion_tag' in d else opn
        usingOpnTag = True if 'opinion_tag' in d else False
        #print(opn, usingOpnTag, file=sys.stderr)
        return Opinion(pTreeName, opn, hd, tg, negCnt, usingOpnTag, volcDict)

    # convert words to index if word vocabulary is given
    def __convertUsingVolcDict__(self):
        if self.volcDict is None:
            return
        
        # if usingOpnTag, then it will not be converted by volcabulary
        if self.volcDict['opinion'] is not None and self.opnW is not None and not self.usingOpnTag:
            self.opn = self.volcDict['opinion'][self.opnW] if self.opnW in self.volcDict['opinion'] else None

        if self.volcDict['holder'] is not None and self.hdW is not None:
            self.hd = self.volcDict['holder'][self.hdW] if self.hdW in self.volcDict['holder'] else None

        if self.volcDict['target'] is not None and self.tgW is not None:
            self.tg = self.volcDict['target'][self.tgW] if self.tgW in self.volcDict['target'] else None

    # negSep=True: divide opinion+/opinion- into to different tuple
    # |O|x|H|x|T|
    def getKeyHOT(self, negSep=False, pTreeSep=False):
        if self.opn is None or self.hd is None or self.tg is None:
            return None
        typeName = 'HOT' if not pTreeSep else ('HOT', self.pTreeName)
        if negSep:
            key = (typeName, self.hd, self.opn, 'sign' + str(self.sign), self.tg)
            return (key, 1)
        else:
            key = (typeName, self.hd, self.opn, self.tg)
            return (key, self.sign)

    # |H|x|T|(x2 or x3)     
    #(O is not found in volcDict is ok because when querying sentiment lexicon, we use original word)
    def getKeyHT(self, sentiDict, negSep=False, ignoreNeutral=False, pTreeSep=False):
        if self.hd is None or self.opnW is None or self.tg is None or sentiDict is None:
            return None
        typeName = 'HT' if not pTreeSep else ('HT', self.pTreeName)

        if self.usingOpnTag:
            key = (typeName, self.hd, self.opn, self.tg)
            return (key, 1)
        sign = self.getSign(sentiDict)
        if negSep:
            if ignoreNeutral and sign == 0:
                return None
            key = (typeName, self.hd, 'sign' + str(sign), self.tg)
            #key = 'HT_%s_^%d_%s' % (self.hd, sign, self.tg)
            return (key, 1)
        else:
            key = (typeName, self.hd, self.tg)
            #key = 'HT_%s_%s' % (self.hd, self.tg)
            return (key, sign)


    # |H|x|O|
    def getKeyHO(self, negSep=False, pTreeSep=False):
        if self.hd is None or self.opn is None or self.tg is None:
            return None
        typeName = 'HO' if not pTreeSep else ('HO', self.pTreeName)
        if negSep:
            key = (typeName, self.hd, 'sign' + str(self.sign), self.opn)
            #key = 'HO_%s_%s^%d' % (self.hd, self.sign, self.opn)
            return (key, 1)
        else:
            key = (typeName, self.hd, self.opn)
            #key = 'HO_%s_%s' % (self.hd, self.opn)
            return (key, self.sign)


    # |H|(x2 or x3)
    def getKeyH(self, sentiDict, negSep=False, ignoreNeutral=False, pTreeSep=False):
        if self.hd is None or self.opnW is None or sentiDict is None:
            return None
        typeName = 'H' if not pTreeSep else ('H', self.pTreeName)
        if self.usingOpnTag:
            key = (typeName, self.hd, self.opn)
            return (key, 1)
        sign = self.getSign(sentiDict)
        if negSep:
            if ignoreNeutral and sign == 0:
                return None
            key = (typeName, self.hd, 'sign' + str(sign))
            #key = 'H_%s^%d' % (self.hd, sign)
            return (key, 1)
        else:
            key = (typeName, self.hd)
            #key = 'H_%s' % (self.hd)
            return (key, sign)
    
    # |O|x|T|
    def getKeyOT(self, negSep=False, pTreeSep=False):
        if self.opn is None or self.tg is None:
            return None
        typeName = 'OT' if not pTreeSep else ('OT', self.pTreeName)
        if negSep:
            key = (typeName, self.opn, 'sign' + str(self.sign), self.tg)
            #key = 'OT_%s^%d_%s' % (self.opn, self.sign, self.tg)
            return (key, 1)
        else:
            key = (typeName, self.opn, self.tg)
            #key = 'OT_%s_%s' % (self.opn, self.tg)
            return (key, self.sign)

    # |T|(x2 or x3)
    def getKeyT(self, sentiDict, negSep=False, ignoreNeutral=False, pTreeSep=False):
        if self.opnW is None or self.tg is None or sentiDict is None:
            return None
        typeName = 'T' if not pTreeSep else ('T', self.pTreeName)
        if self.usingOpnTag:
            key = (typeName, self.tg, self.opn)
            return (key, 1)
        sign = self.getSign(sentiDict)
        if negSep:
            if ignoreNeutral and sign == 0:
                return None
            key = (typeName, self.tg, 'sign' + str(sign))
            #key = 'T_%s^%d' % (self.tg, sign)
            return (key, 1)
        else:
            key = (typeName, self.tg)
            #key = 'T_%s' % (self.tg)
            return (key, sign)
        
    def getSign(self, sentiDict=None):
        if sentiDict == None:
            return self.sign # +1/-1
        else:
            sign = self.sign * sentiDict[self.opnW] if (self.opnW in sentiDict) else 0
            sign = 1 if sign > 0 else (-1 if sign < 0 else 0) 
            return sign #+1/0/-1

    def __repr__(self):
        tmp = dict()
        tmp['holder'] = self.hd
        tmp['target'] = self.tg
        tmp['opinion'] = self.opn
        tmp['sign'] = self.sign
        return '%s' % (tmp)
