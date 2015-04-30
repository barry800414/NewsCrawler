

# This class represent an opinion, which consists of 
# holder, opinion and target(but some of them can be
# None)
# O: opinion
# H: holder
# T: target
# N: negation (to opinion)
class Opinion():
    def __init__(self, opinion, holder, target, negCnt=0):
        self.opn = opinion
        self.hd = holder
        self.tg = target
        self.negCnt = negCnt
        self.sign = 1 if negCnt % 2 == 0 else -1
    
    # negSep=True: divide opinion+/opinion- into to different tuple
    # |O|x|H|x|T|(x2)
    def getTupleHOT(self, negSep=False):
        if self.opn == None or self.hd == None or self.tg == None:
            return None
        if negSep:
            key = '%s_%s^%d_%s' % (self.hd, self.opn, 
                    self.sign, self.tg)
            return (key, 1)
        else:
            key = '%s_%s_%s' % (self.hd, self.opn, self.tg)
            return (key, self.sign)

    # |H|x|T|(x2)
    def getTupleHT(self, sentiDict, negSep=False):
        if self.hd == None or self.opn == None or self.tg == None or sentiDict == None:
            return None
        sign = self.getSign(sentiDict)
        if negSep:
            key = '%s_%d_%s' % (self.hd, sign, self.tg)
            return (key, 1)
        else:
            key = '%s_%s' % (self.hd, self.tg)
            return (key, sign)

    # |H|(x2)
    def getTupleH(self, sentiDict, negSep=False):
        if self.hd == None or self.opn == None or sentiDict == None:
            return None
        sign = self.getSign(sentiDict)
        if negSep:
            key = '%s^%d' % (self.hd, sign)
            return (key, 1)
        else:
            key = '%s' % (self.hd)
            return (key, sign)
    
    # |O|x|T|(x2)
    def getTupleOT(self, negSep=False):
        if self.opn == None or self.target == None or sentiDict == None:
            return None
        if negSep:
            key = '%s^%d_%s' % (self.opn, self.sign, self.tg)
            return (key, 1)
        else:
            key = '%s_%s' % (self.opn, self.tg)
            return (key, self.sign)

    # |T|(x2)
    def getTupleT(self, sentiDict, negSep=False):
        if self.opn == None or self.target == None or sentiDict == None:
            return None
        sign = self.getSign(sentiDict)
        if negSep:
            key = '%s^%d' % (self.tg, sign)
            return (key, 1)
        else:
            key = '%s' (self.tg)
            return (key, sign)
        
    def getSign(self, sentiDict=None):
        if sentiDict == None:
            return self.sign # +1/-1
        else:
            sign = self.sign * sentiDict[self.opn] if (self.opn in sentiDict) else 0
            sign = 1 if sign > 0 else (-1 if sign < 0 else 0) 
            return sign #+1/0/-1


