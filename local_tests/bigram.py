#!/usr/bin/env python

import nltk
from nltk.corpus import stopwords
from nltk.collocations import *
import sys
import string

reload(sys)
sys.setdefaultencoding('utf-8')

bullfile = sys.argv[1]
ofile = sys.argv[2]
 
stop_words = set(stopwords.words('english'))

f = open(bullfile)
raw = f.read()

tokens = nltk.word_tokenize(raw)

bigram_measures = nltk.collocations.BigramAssocMeasures()

punc = string.punctuation

finder = BigramCollocationFinder.from_words(tokens)
finder.apply_freq_filter(2)
finder.apply_word_filter(lambda x: x in punc)
finder.apply_word_filter(lambda x: x in stop_words)
print(finder.nbest(bigram_measures.pmi,30))

# fdist = nltk.FreqDist(finder)
# with open(ofile,'w+') as of:
# 	for k,v in fdist.items():
# 		of.write(str(k))
# 		of.write(str(v))
# 		of.write('\n')