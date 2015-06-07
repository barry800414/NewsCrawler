

# This class represent an opinion, which consists of 
# holder, opinion and target(but some of them can be
# None)
# O: opinion
# H: holder
# T: target
# N: negation (to opinion)
class Opinion():
    def __init__(self, opinion=None, holder=None, target=None, negCnt=0, 
            volcDict=None):
        # original word
        self.opnW = opinion 
        self.hdW = holder
        self.tgW = target
        # word(no sentiDict) or index(with sentiDict)
        self.opn = opinion
        self.hd = holder
        self.tg = target
        self.negCnt = negCnt
        self.sign = 1 if negCnt % 2 == 0 else -1
        self.volcDict = volcDict
        self.__convertUsingVolcDict__()

    def genOpnFromDict(d, volcDict):
        opn = d['opinion'] if 'opinion' in d else None
        hd = d['holder'] if 'holder' in d else None
        tg = d['target'] if 'target' in d else None
        negCnt = d['neg']['opinion'] if 'neg' in d and 'opinion' in d['neg'] else 0
        return Opinion(opn, hd, tg, negCnt, volcDict)

    # convert words to index if word vocabulary is given
    def __convertUsingVolcDict__(self):
        if self.volcDict is None:
            return
        if self.volcDict['opinion'] is None:
            self.opn = self.opnW
        else:
            if self.opnW is not None:
                self.opn = self.volcDict['opinion'][self.opnW] if self.opnW in self.volcDict['opinion'] else None
        if self.volcDict['holder'] is None:
            self.hd = self.hdW
        else:
            if self.hdW is not None:
                self.hd = self.volcDict['holder'][self.hdW] if self.hdW in self.volcDict['holder'] else None
        if self.volcDict['target'] is None:
            self.tg = self.tgW
        else:
            if self.tgW is not None:
                self.tg = self.volcDict['target'][self.tgW] if self.tgW in self.volcDict['target'] else None

    # negSep=True: divide opinion+/opinion- into to different tuple
    # |O|x|H|x|T|(x2)
    def getKeyHOT(self, negSep=False):
        if self.opn == None or self.hd == None or self.tg == None:
            return None
        if negSep:
            key = ('HOT', self.hd, self.opn, 'sign' + str(self.sign), self.tg)
            #key = 'HOT_%s_%s^%d_%s' % (self.hd, self.opn, 
            #        self.sign, self.tg)
            return (key, 1)
        else:
            key = ('HOT', self.hd, self.opn, self.tg)
            #key = 'HOT_%s_%s_%s' % (self.hd, self.opn, self.tg)
            return (key, self.sign)

    # |H|x|T|(x2)
    def getKeyHT(self, sentiDict, negSep=False):
        if self.hd == None or self.opn == None or self.tg == None or sentiDict == None:
            return None
        sign = self.getSign(sentiDict)
        if negSep:
            key = ('HT', self.hd, 'sign' + str(sign), self.tg)
            #key = 'HT_%s_^%d_%s' % (self.hd, sign, self.tg)
            return (key, 1)
        else:
            key = ('HT', self.hd, self.tg)
            #key = 'HT_%s_%s' % (self.hd, self.tg)
            return (key, sign)


    # |H|x|T|(x2)
    def getKeyHO(self, negSep=False):
        if self.hd == None or self.opn == None or self.tg == None:
            return None
        if negSep:
            key = ('HO', self.hd, 'sign' + str(self.sign), self.opn)
            #key = 'HO_%s_%s^%d' % (self.hd, self.sign, self.opn)
            return (key, 1)
        else:
            key = ('HO', self.hd, self.opn)
            #key = 'HO_%s_%s' % (self.hd, self.opn)
            return (key, self.sign)


    # |H|(x2)
    def getKeyH(self, sentiDict, negSep=False):
        if self.hd == None or self.opn == None or sentiDict == None:
            return None
        sign = self.getSign(sentiDict)
        if negSep:
            key = ('H', self.hd, 'sign' + str(sign))
            #key = 'H_%s^%d' % (self.hd, sign)
            return (key, 1)
        else:
            key = ('H', self.hd)
            #key = 'H_%s' % (self.hd)
            return (key, sign)
    
    # |O|x|T|(x2)
    def getKeyOT(self, negSep=False):
        if self.opn == None or self.tg == None:
            return None
        if negSep:
            key = ('OT', self.opn, 'sign' + str(self.sign), self.tg)
            #key = 'OT_%s^%d_%s' % (self.opn, self.sign, self.tg)
            return (key, 1)
        else:
            key = ('OT', self.opn, self.tg)
            #key = 'OT_%s_%s' % (self.opn, self.tg)
            return (key, self.sign)

    # |T|(x2)
    def getKeyT(self, sentiDict, negSep=False):
        if self.opn == None or self.tg == None or sentiDict == None:
            return None
        sign = self.getSign(sentiDict)
        if negSep:
            key = ('T', self.tg, 'sign' + str(sign))
            #key = 'T_%s^%d' % (self.tg, sign)
            return (key, 1)
        else:
            key = ('T', self.tg)
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
