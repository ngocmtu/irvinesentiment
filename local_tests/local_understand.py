#!/usr/bin/env python

import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from nltk.collocations import BigramCollocationFinder, BigramAssocMeasures
from nltk.tokenize import word_tokenize
from nltk import bigrams 
from nltk import FreqDist
import sys
import csv
from nltk.corpus import stopwords
from os import path, listdir

stop_words=set(stopwords.words('english'))
nltk.download('punkt')
reload(sys)
sys.setdefaultencoding('utf-8')
 
def word_feats(words):
    return dict([(word, True) for word in words])

def best_bigram_word_feats(words,score_fn=BigramAssocMeasures.chi_sq,n=1000):
	bigram_finder = BigramCollocationFinder.from_words(words)
	bigram_finder.apply_word_filter(lambda w: not w.isalpha())
	bigram_finder.apply_word_filter(lambda w: w in stop_words)
	bigram_finder.apply_word_filter(lambda w: len(w)<2)

	bigrams = bigram_finder.nbest(score_fn,n)
	d = dict([(bigram, True) for bigram in bigrams])

	single_words = [word.lower() for index,word in enumerate(words) if len(word) > 3 and not word.isdigit() and not word in stop_words and words[index-1]!='$' and words[index-1]!='@']
	d.update(word_feats(single_words))
	return d

# get all files from folder
folder = sys.argv[1]
files = listdir(folder)
files = [f for f in files if f[-3:len(f)]=='csv']
bulltwits = []
beartwits = []

# extract content of folder into two lists
# one containing all bull twits
# the other all bear twits
for f in files:
	with open(path.join(folder,f),'r') as csvfile:
		reader = csv.reader(csvfile)
		if f.find('bull') > -1:
			for row in reader:
				bulltwits.append(row[1])
		elif f.find('bear') > -1:
			for row in reader:
				beartwits.append(row[1])
		else:
			continue

bull_words = []
bear_words = []

# because there's more bearish news
# limit the length of bullish list to its bearish list
total_bear_tweets = len(beartwits)
bulltwits = bulltwits[:total_bear_tweets]

for line in bulltwits:
	line = unicode(line,errors='ignore')
	bull_words.append(word_tokenize(line.lower()))
for line in beartwits:
	line = unicode(line,errors='ignore')
	bear_words.append(word_tokenize(line.lower()))

# BigramCollocationFinder.from_words takes param of list of words
bull_feats = [(best_bigram_word_feats(bull_word),'bull') for bull_word in bull_words]
bear_feats = [(best_bigram_word_feats(bear_word),'bear') for bear_word in bear_words]

bull_cutoff = int(len(bull_feats)*0.9)
bear_cutoff = int(len(bear_feats)*0.9)

trainfeats = bull_feats[:bull_cutoff] + bear_feats[:bear_cutoff]
testfeats = bull_feats[bull_cutoff:] + bear_feats[bear_cutoff:]

classifier = NaiveBayesClassifier.train(trainfeats)
classifier.show_most_informative_features(100)

print 'accuracy:', nltk.classify.util.accuracy(classifier, testfeats)