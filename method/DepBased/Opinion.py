

# This class represent an opinion, which consists of 
# holder, opinion and target(but some of them can be
# None)
# O: opinion
# H: holder
# T: target
# N: negation (to opinion)
class Opinion():
    def __init__(self, opinion=None, holder=None, target=None, negCnt=0, 
            wVolc=None):
        self.opn = opinion
        self.hd = holder
        self.tg = target
        self.negCnt = negCnt
        self.sign = 1 if negCnt % 2 == 0 else -1
        self.wVolc = wVolc
        self.__convertUsingWVolc__()

    def genOpnFromDict(d, wVolc=None):
        opn = d['opinion'] if 'opinion' in d else None
        hd = d['holder'] if 'holder' in d else None
        tg = d['target'] if 'target' in d else None
        negCnt = d['neg']['opinion'] if 'neg' in d and 'opinion' in d['neg'] else 0
        return Opinion(opn, hd, tg, negCnt, wVolc)

    # convert words to index if word vocabulary is given
    def __convertUsingWVolc__(self):
        if self.wVolc == None:
            return
        if self.opn != None:
            self.opn = str(self.wVolc[self.opn]) if self.opn in self.wVolc else None
        if self.hd != None:
            self.hd = str(self.wVolc[self.hd]) if self.hd in self.wVolc else None
        if self.tg != None:
            self.tg = str(self.wVolc[self.tg]) if self.tg in self.wVolc else None

    # negSep=True: divide opinion+/opinion- into to different tuple
    # |O|x|H|x|T|(x2)
    def getKeyHOT(self, negSep=False):
        #if self.opn == None or self.hd == None or self.tg == None:
        #    return None
        if negSep:
            key = 'HOT_%s_%s^%d_%s' % (self.hd, self.opn, 
                    self.sign, self.tg)
            return (key, 1)
        else:
            key = 'HOT_%s_%s_%s' % (self.hd, self.opn, self.tg)
            return (key, self.sign)

    # |H|x|T|(x2)
    def getKeyHT(self, sentiDict, negSep=False):
        #if self.hd == None or self.opn == None or self.tg == None or sentiDict == None:
        #    return None
        sign = self.getSign(sentiDict)
        if negSep:
            key = 'HT_%s_^%d_%s' % (self.hd, sign, self.tg)
            return (key, 1)
        else:
            key = 'HT_%s_%s' % (self.hd, self.tg)
            return (key, sign)


    # |H|x|T|(x2)
    def getKeyHO(self, negSep=False):
        #if self.hd == None or self.opn == None or self.tg == None:
        #    return None
        if negSep:
            key = 'HO_%s_%s^%d' % (self.hd, self.sign, self.opn)
            return (key, 1)
        else:
            key = 'HO_%s_%s' % (self.hd, self.opn)
            return (key, self.sign)


    # |H|(x2)
    def getKeyH(self, sentiDict, negSep=False):
        #if self.hd == None or self.opn == None or sentiDict == None:
        #    return None
        sign = self.getSign(sentiDict)
        if negSep:
            key = 'H_%s^%d' % (self.hd, sign)
            return (key, 1)
        else:
            key = 'H_%s' % (self.hd)
            return (key, sign)
    
    # |O|x|T|(x2)
    def getKeyOT(self, negSep=False):
        #if self.opn == None or self.target == None or sentiDict == None:
        #    return None
        if negSep:
            key = 'OT_%s^%d_%s' % (self.opn, self.sign, self.tg)
            return (key, 1)
        else:
            key = 'OT_%s_%s' % (self.opn, self.tg)
            return (key, self.sign)

    # |T|(x2)
    def getKeyT(self, sentiDict, negSep=False):
        #if self.opn == None or self.target == None or sentiDict == None:
        #    return None
        sign = self.getSign(sentiDict)
        if negSep:
            key = 'T_%s^%d' % (self.tg, sign)
            return (key, 1)
        else:
            key = 'T_%s' % (self.tg)
            return (key, sign)
        
    def getSign(self, sentiDict=None):
        if sentiDict == None:
            return self.sign # +1/-1
        else:
            sign = self.sign * sentiDict[self.opn] if (self.opn in sentiDict) else 0
            sign = 1 if sign > 0 else (-1 if sign < 0 else 0) 
            return sign #+1/0/-1

    def __repr__(self):
        tmp = dict()
        tmp['holder'] = self.hd
        tmp['target'] = self.tg
        tmp['opinion'] = self.opn
        tmp['sign'] = self.sign
        tmp['hasWVolc'] = True if self.wVolc != None else False
        return '%s' % (tmp)
