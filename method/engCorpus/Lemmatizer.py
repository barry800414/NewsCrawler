
import re

import nltk
from nltk.stem.wordnet import WordNetLemmatizer


lmtzr = WordNetLemmatizer()

WORD_SEP = ' '
TAG_SEP = '/'

# For new tags mapping: 
# Key is original POS Tag (Penn Treebank https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html )
# Value is new POS Tag: simplified by prefix (e.g. JJR-> JJ)
NEW_TAG_MAP = {
        "JJ": "JJ", "JJR": "JJ", "JJS": "JJ",
        "NN": "NN", "NNP": "NNP", "NNPS": "NNP", "NNS": "NN",
        "RB": "RB", "RBR": "RB", "RBS": "RB",
        "VB": "VB", "VBD": "VB", "VBG": "VB", "VBN": "VB", "VBP": "VB", "VBZ": "VB"
        }

# For tags mapping for wordnet lemmatizer:
# Key is original POS Tag
# Value is abbreviation in wordnet module in nltk

#{ Part-of-speech constants
#ADJ, ADJ_SAT, ADV, NOUN, VERB = 'a', 's', 'r', 'n', 'v'
#}
LMTZR_TAG_MAP = {
        "JJ": "a", "JJR": "a", "JJS": "a",
        "NN": "n", "NNP": "n", "NNPS": "n", "NNS": "n",
        "RB": "r", "r": "r", "r": "r",
        "VB": "v", "VBD": "v", "VBG": "v", "VBN": "v", "VBP": "v", "VBZ": "v"
        }

# sent: the words in sent should be tagged by Penn TreeBank tag set
# e.g. he/PRP had/VBD cars/NNS
def lemmatizeTaggedSent(sent, wordSep=WORD_SEP, tagSep=TAG_SEP):
    outStr = ''
    for wt in sent.split(wordSep):
        (w, t) = wt.split(tagSep)
        if t not in LMTZR_TAG_MAP:
            newWt = wt
        else:
            newWt = lmtzr.lemmatize(w, pos=LMTZR_TAG_MAP[t]) + tagSep + NEW_TAG_MAP[t]
        if len(outStr) == 0:
            outStr = str(newWt)
        else:
            outStr = outStr + wordSep + newWt
    return outStr

#print(lemmatizeTaggedSent('he/PRP had/VBD cars/NNS'))
