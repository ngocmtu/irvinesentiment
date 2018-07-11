#!/usr/bin/env python

import sys
import csv
from os import path, listdir
from nltk.classify.util import accuracy
from nltk.classify import NaiveBayesClassifier
from nltk.collocations import BigramCollocationFinder, BigramAssocMeasures
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import cPickle as pickle

stop_words=set(stopwords.words('english'))
reload(sys)
sys.setdefaultencoding('utf-8')

folder = sys.argv[1]
files = sorted(listdir(folder))
stock_tickers = [line.rstrip('\n\r') for line in open('tick2015.csv')]
stock_tickers = [tick.lower() for tick in stock_tickers]

def word_feats(words):
    return dict([(word, True) for word in words])

bigram_measure = BigramAssocMeasures()
def best_bigram_word_feats(words,score_fn=bigram_measure.pmi,n=1000):
	bigram_finder = BigramCollocationFinder.from_words(words)
	bigram_finder.apply_word_filter(lambda w: not w.isalpha())
	bigram_finder.apply_word_filter(lambda w: w in stop_words)
	bigram_finder.apply_word_filter(lambda w: len(w)<2)

	bigrams = bigram_finder.nbest(score_fn,n)
	d = dict([(bigram, True) for bigram in bigrams])

	single_words = [word.lower() for index,word in enumerate(words) if len(word) > 3 and not word.isdigit() and not word in stop_words and words[index-1]!='$' and words[index-1]!='@']
	d.update(word_feats(single_words))
	return d

def filter_stock(tweet):
	words = tweet.split()
	return_words = []
	for word in words:
		if word[0] == '$' and word[1:] not in stock_tickers:
			return None
		else:
			return_words.append(word)
	return return_words

# input: csv file reader
# output: a list of tuple; each tuple is a tokenized tweet and its associated sentiment
def get_feats(reader,sen):
	words = []
	for row in reader:
		tweet = row[1]
		filtered = filter_stock(tweet)
		words.append(filtered) if filtered is not None else None
	return [(best_bigram_word_feats(word),sen) for word in words]

classifier = None
if path.isfile('save_classifier.p'):
	classifier = pickle.load(open('save_classifier.p','r'))
	print('Classifier loaded')

bear_count = 0
bull_count = 0
test_feats = []

# extract content of folder into two lists
# one containing all bull twits
# the other all bear twits
for f in files:
	with open(path.join(folder,f),'r') as csvfile:
		reader = csv.reader(csvfile)
		if f.find('bear') > -1:
			test_feats += get_feats(reader,'bear')
			total = len(test_feats)
			for feat in test_feats:
				sen = classifier.classify(feat[0])
				if sen == 'bear':
					bear_count += 1
			print('total '+str(total)+' bear count: '+str(bear_count))
			print('Test on '+str(f)+' | Accuracy: '+str(accuracy(classifier,test_feats)))
		elif f.find('bull') > -1:
			test_feats += get_feats(reader,'bull')
			total = len(test_feats)
			for feat in test_feats:
				sen = classifier.classify(feat[0])
				if sen == 'bull':
					bull_count += 1
				#print(str(feat) + ' '+str(sen))
			print('total '+str(total)+' bull count: '+str(bull_count))
			print('Test on '+str(f)+' | Accuracy: '+str(accuracy(classifier,test_feats)))
print('Accuracy: '+str(accuracy(classifier,test_feats)))