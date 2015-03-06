

# default sentence separator
SEP = '[,;\t\n，。；　「」﹝﹞【】《》〈〉（）〔〕『 』\(\)\[\]!?？！\u2019 ]'


# default to-removed punctuation
TO_REMOVE = '[\uF0D8\u0095/=&�+、:：／\|‧]'

# default brackets for fixing them (not to segment)
BRACKETS = [ ('[', ']'), ('(', ')'), ('{', '}'), 
             ('〈', '〉'), ('《', '》'), ('【', '】'),
             ('﹝', '﹞'), ('「','」'), ('『', '』'), 
             ('（','）'), ('〔','〕')]


SEP2 = '[,;\t\n，。；　「」﹝﹞【】《》〈〉（）〔〕『 』\(\)\[\]!?？！]'

# default to-removed punctuation
TO_REMOVE2 = '[\uF0D8\u0095/=&�+、:：／\|‧]'



puncSet = set()

for c in SEP:
    puncSet.add(c)
for c in SEP2:
    puncSet.add(c)
for c in TO_REMOVE:
    puncSet.add(c)
for c in TO_REMOVE2:
    puncSet.add(c)
for b in BRACKETS:
    puncSet.add(b[0])
    puncSet.add(b[1])

puncList = list(puncSet)
puncList.sort()

for c in puncList:
    print(c, ':', hex(ord(c)))    
