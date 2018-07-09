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

# get all files from folder
folder = sys.argv[1]
files = listdir(folder)
files = [f for f in files if f[-3:len(f)]=='csv']
classifier = None

# if classifier already pickled, unpickle
# if not, get bull, bear features, train classifer and then pickle for future uses
if path.isfile('save_classifier.p'):
	classifier = pickle.load(open('save_classifier.p','r'))
	print('Classifier loaded')
else:
	print('Classifier not saved, making a new one')
	# lists that store bullish, bearish, and no sentiment twits
	bulltwits = []
	beartwits = []
	nosentwits = []

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

	bull_words = []
	bear_words = []

	# filter out twits that do not mention stocks
	# tokenize twits into lists of single words
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
	
	# write out result to pickle files for easy future access
	trainfeats = bull_feats + bear_feats
	classifier = NaiveBayesClassifier.train(trainfeats)
	pickle.dump(classifier,open('save_classifier.p','wb'))
	

for f in files:
	nosen_num = f.find('nosen')
	classfied_file_name = f[:nosen_num]+'classified.csv'

	# if there's a 'nosen.csv', gather unclassified data and calculate the probability of it being bull or bear
	# if there's none, move along
	if nosen_num > -1 and not path.isfile(classfied_file_name):
		with open(path.join(folder,f),'r') as csvread, open(classfied_file_name,'wb') as csvwrite:
			reader = csv.reader(csvread)
			writer = csv.writer(csvwrite)
			writer.writerow(['created_at','tweet','ticker','probability','sentiment'])

			for row in reader:
				line = unicode(row[1],errors='ignore')
				to_append = filter_stock(word_tokenize(line.lower()))
				if to_append is not None:
					created_at = row[0]
					probdist = classifier.prob_classify(best_bigram_word_feats(to_append))
					samples = probdist.samples()
					tickers = get_ticker(line)
					for sample in samples:
						for ticker in tickers:
							writer.writerow([created_at,line,ticker,probdist.prob(sample),sample])
