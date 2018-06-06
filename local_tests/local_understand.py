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
reload(sys)
sys.setdefaultencoding('utf-8')
stock_tickers = [line.rstrip('\n\r') for line in open('tick2015.csv')]
stock_tickers = [tick.lower() for tick in stock_tickers]
bigram_measure = BigramAssocMeasures()
 
def word_feats(words):
    return dict([(word, True) for word in words])

def best_bigram_word_feats(words,score_fn=bigram_measure.pmi,n=2000):
	bigram_finder = BigramCollocationFinder.from_words(words)
	bigram_finder.apply_word_filter(lambda w: not w.isalpha())
	bigram_finder.apply_word_filter(lambda w: w in stop_words)
	bigram_finder.apply_word_filter(lambda w: len(w)<2)
	bigram_finder.apply_word_filter(lambda w: w in stock_tickers)
	bigram_finder.apply_word_filter(lambda w: w == 'http')

	bigrams = bigram_finder.nbest(score_fn,n)
	d = dict([(bigram, True) for bigram in bigrams])

	single_words = [word.lower() for index,word in enumerate(words) if len(word) > 1 and word.isalpha() and not word in stop_words and words[index-1]!='$' and words[index-1]!='@']
	# 
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

def filter_stock(words):
	return_words = []
	for index,word in enumerate(words):
		if words[index-1] == '$' and word.isalpha() and not word in stock_tickers:
			return None
		else:
			return_words.append(word)
	return return_words


for line in bulltwits:
	line = unicode(line,errors='ignore')
	to_append = filter_stock(word_tokenize(line.lower()))
	bull_words.append(to_append) if to_append is not None else None
	# bull_words.append(word_tokenize(line.lower()))
for line in beartwits:
	line = unicode(line,errors='ignore')
	to_append = filter_stock(word_tokenize(line.lower()))
	bear_words.append(to_append) if to_append is not None else None
	# bear_words.append(word_tokenize(line.lower()))

#BigramCollocationFinder.from_words takes param of list of words
bull_feats = [(best_bigram_word_feats(bull_word),'bull') for bull_word in bull_words]
bear_feats = [(best_bigram_word_feats(bear_word),'bear') for bear_word in bear_words]

accuracy_from_tests = []
for i in range(10):
	i = 0.1*i
	bull_cutoff = int(len(bull_feats)*i)
	bear_cutoff = int(len(bear_feats)*i)
	bull_cutoff_up = int(len(bull_feats)*(i+0.1))
	bear_cutoff_up = int(len(bear_feats)*(i+0.1))


	trainfeats = bull_feats[0:bull_cutoff] + bull_feats[bull_cutoff_up:len(bull_feats)] + bear_feats[0:bear_cutoff] + bear_feats[bear_cutoff_up:len(bear_feats)]
	testfeats = bull_feats[bull_cutoff:bull_cutoff_up] + bear_feats[bear_cutoff:bear_cutoff_up]

	classifier = NaiveBayesClassifier.train(trainfeats)
	classifier.show_most_informative_features(100)

	test_accuracy = nltk.classify.util.accuracy(classifier, testfeats)
	accuracy_from_tests.append(test_accuracy)
	print('Trained on '+str(len(trainfeats))+' rows')
	print('Tested on '+str(len(testfeats))+' rows')
	print('Test number %i accuracy: %f' % (i*10+1, test_accuracy))

print('The average accuracy of 10 tests is '+str(sum(accuracy_from_tests)/len(accuracy_from_tests)))