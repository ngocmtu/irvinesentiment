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
import cPickle as pickle

###################################################################
# VARIABLE INITIALIZATION
###################################################################

stop_words=set(stopwords.words('english'))
reload(sys)
sys.setdefaultencoding('utf-8')
stock_tickers = [line.rstrip('\n\r') for line in open('tick2015.csv')]
stock_tickers = [tick.lower() for tick in stock_tickers]
bigram_measure = BigramAssocMeasures()
 
# turn list of words into features
def word_feats(words):
    return dict([(word, True) for word in words])

def single_word_filter(words):
	return [word.lower() for index,word in enumerate(words) if len(word) > 1 and word.isalpha() and not word in stop_words and words[index-1]!='$' and words[index-1]!='@']

# turn list of words into list of features with bigrams and single words attached to each other
def best_bigram_word_feats(words,score_fn=bigram_measure.pmi,n=2000):
	bigram_finder = BigramCollocationFinder.from_words(words)
	bigram_finder.apply_word_filter(lambda w: not w.isalpha())
	bigram_finder.apply_word_filter(lambda w: w in stop_words)
	bigram_finder.apply_word_filter(lambda w: len(w)<2)
	bigram_finder.apply_word_filter(lambda w: w in stock_tickers)
	bigram_finder.apply_word_filter(lambda w: w == 'http')

	bigrams = bigram_finder.nbest(score_fn,n)
	d = dict([(bigram, True) for bigram in bigrams])

	single_words = single_word_filter(words)
	d.update(word_feats(single_words))
	return d

# only include only twits that mention stocks
# everything is not included
def filter_stock(words):
	return_words = []
	for index,word in enumerate(words):
		if words[index-1] == '$' and word.isalpha() and not word in stock_tickers:
			return None
		else:
			return_words.append(word)
	return return_words

# input: tweet ('$AAPL and $FB are rocketing!')
# output: a list of tickers from the tweet (['$AAPL','$FB'])
def get_ticker(tweet):
	words = tweet.split()
	return [word.upper() for word in words if word[0] == '$' and word[1:].lower() in stock_tickers]

###################################################################
# MAIN PROGRAM
###################################################################

def get_classifier():
	classifier = None
	while True:
		build_or_use_existing = raw_input('Would you like to load an existing classifier (2015 data) or build a new one?(load/build/break) \n')

		# if user chose not to load or build 
		# exit the program
		if build_or_use_existing == 'break':
			break

		# build classifier
		# take a folder of labeled training data
		elif build_or_use_existing == 'build':
			print('Building your classifier!')
			new_classifier_name = raw_input('Please name the new classifier \n')
			new_classifier_name = new_classifier_name+'.p'
			files = listdir('training_data')
			files = [file for file in files if file != '.keep']
			if files == []:
				print('training_data folder empty, exiting program')
				break
			else:
				bull_words = []
				bear_words = []

				# extract content of folder into two lists
				# one containing all bull twits
				# the other all bear twits
				for f in files:
					with open(path.join('training_data',f),'r') as csvfile:
						reader = csv.reader(csvfile)
						if f.find('bull') > -1:
							for row in reader:
								twit = unicode(row[1],errors='ignore')
								to_append = filter_stock(word_tokenize(twit.lower()))
								bull_words.append(to_append) if to_append is not None else None
						elif f.find('bear') > -1:
							for row in reader:
								twit = unicode(row[1],errors='ignore')
								to_append = filter_stock(word_tokenize(twit.lower()))
								bear_words.append(to_append) if to_append is not None else None

				# BigramCollocationFinder.from_words takes param of list of words
				bull_feats = [(best_bigram_word_feats(bull_word),'bull') for bull_word in bull_words]
				bear_feats = [(best_bigram_word_feats(bear_word),'bear') for bear_word in bear_words]
				
				# write out result to pickle files for easy future access
				trainfeats = bull_feats + bear_feats
				classifier = NaiveBayesClassifier.train(trainfeats)
				pickle.dump(classifier,open(new_classifier_name,'wb'))

				print('Classifier built! Saved in '+new_classifier_name)
				break

		# if user types "load" or nothing at all:
		# load classifier trained by 2015 data
		else:
			if path.isfile('save_classifier.p'):
				classifier = pickle.load(open('save_classifier.p','r'))
				print('Classifier loaded')
				break
			else:
				print('No default classifier, please include a pickled classifier in this folder and try again')
				continue

	return classifier