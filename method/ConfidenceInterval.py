
import numpy as np
import scipy as sp
import scipy.stats
import math

def meanConfidenceInterval(data, confidence=0.95):
    n = len(data)
    if n >= 30:
        mean, stdev = np.mean(data), np.std(data)
    else:
        mean, stdev = np.mean(data), np.std(data, ddof=1)
    return calcConfidenceInterval(mean, stdev, n)

def calcConfidenceInterval(mean, stdev, nSamples, confidence=0.95):
    n = nSamples
    if n >= 30:
        # using normal distribution
        interval = sp.stats.norm.ppf(1-(1-confidence)/2.) * stdev / np.sqrt(n)
    else:
        # using student-t distribution
        interval = sp.stats.t._ppf(1-(1-confidence)/2., n-1) * stdev / np.sqrt(n)
    return interval

#print(meanConfidenceInterval([1, 2, 4, 10]))
#print(test([1, 2, 4, 10]))
#calcConfidenceInterval(1, 2, 3)
