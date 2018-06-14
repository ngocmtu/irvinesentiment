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

# param: 
# # tweets: list of tweets, each tweet has str type
# # filename: input file name to name the output file
# classify input list of tweets, write them to an output file

# TODO: find out how to turn bigrams in regular words and use them as features
# def classify_nosen(tweets, filename):
# 	nosen_words = None
# 	nosentwits_filtered = None
# 	for tweet in tweets:
# 		tweet = unicode(tweet,errors='ignore')
# 		to_append = filter_stock(word_tokenize(tweet.lower()))
# 		if to_append is not None:

# 		nosen_words.append(to_append) if to_append is not None else None
# 		nosentwits_filtered.append(line) if to_append is not None else None

# 		nosen_feats = [word_feats(single_word_filter(nosen_word)) for nosen_word in nosen_words]

# get all files from folder
folder = sys.argv[1]
files = listdir(folder)
files = [f for f in files if f[-3:len(f)]=='csv']
classifier = None

# if classifier already pickled, unpickle
# if not, get bull, bear features, train classifer and then pickle for future uses
if path.isfile('save_classifier.p'):
	classifier = pickle.load(open('save_classifier.p','r'))
else:
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
	if nosen_num > -1 and not path.isfile(classfied_file_name):
		with open(path.join(folder,f),'r') as csvread, open(classfied_file_name,'wb') as csvwrite:
			reader = csv.reader(csvread)
			writer = csv.writer(csvwrite)
			writer.writerow(['tweet','probability','sentiment'])

			for row in reader:
				line = unicode(row[1],errors='ignore')
				to_append = filter_stock(word_tokenize(line.lower()))
				if to_append is not None:
					probdist = classifier.prob_classify(best_bigram_word_feats(to_append))
					samples = probdist.samples()
					for sample in samples:
						writer.writerow([line,probdist.prob(sample),sample])

			# 	for line in nosentwits:
# 		line = unicode(line,errors='ignore')
# 		to_append = filter_stock(word_tokenize(line.lower()))
# 		nosen_words.append(to_append) if to_append is not None else None
# 		nosentwits_filtered.append(line) if to_append is not None else None



# with open('nosen_classified.csv','wb') as csvfile:
# 	writer = csv.writer(csvfile)
# 	writer.writerow(['tweet','probability','sentiment'])
# 	for original,feat in zip(nosentwits_filtered, nosen_feats):
# 		probdist = classifier.prob_classify(feat)
# 		samples = probdist.samples()
# 		for sample in samples:
# 			writer.writerow([original,probdist.prob(sample),sample])




# 	nosen_feats = pickle.load(open('save_nosen.p','r'))
# 	nosentwits_filtered = pickle.load(open('save_nosen_filtered.p','r'))

# 	nosen_words = []

	

	

# 	pickle.dump(nosen_feats,open('save_nosen.p','wb'))
# 	pickle.dump(nosentwits_filtered,open('save_nosen_filtered.p','wb'))

# for feat in nosen_feats[:6]:
# 	probdist = classifier.prob_classify(feat)
# 	samples = probdist.samples()
# 	for sample in samples:
# 		#print(sample)
# 		print(str(feat) + str(probdist.prob(sample)) + ' ' + str(sample))

# accuracy_from_tests = []
# for i in range(10):
# 	i = 0.1*i
# 	bull_cutoff = int(len(bull_feats)*i)
# 	bear_cutoff = int(len(bear_feats)*i)
# 	bull_cutoff_up = int(len(bull_feats)*(i+0.1))
# 	bear_cutoff_up = int(len(bear_feats)*(i+0.1))


# 	trainfeats = bull_feats[0:bull_cutoff] + bull_feats[bull_cutoff_up:len(bull_feats)] + bear_feats[0:bear_cutoff] + bear_feats[bear_cutoff_up:len(bear_feats)]
# 	testfeats = bull_feats[bull_cutoff:bull_cutoff_up] + bear_feats[bear_cutoff:bear_cutoff_up]

# 	classifier = NaiveBayesClassifier.train(trainfeats)
# 	# classifier.show_most_informative_features(100)


# 	for each in nosen_feats:
# 		print(str(each)+': '+classifier.classify(each))

	# test_accuracy = nltk.classify.util.accuracy(classifier, testfeats)
	# accuracy_from_tests.append(test_accuracy)
# 	print('Trained on '+str(len(bull_feats)*0.9)+' bull rows and '+str(len(bear_feats)*0.9)+' bear rows')
# 	print('Tested on '+str(len(bull_feats)*0.1)+' bull rows and '+str(len(bear_feats)*0.1)+' bear rows')
# 	print('Test number %i accuracy: %f' % (i*10+1, test_accuracy))

# print('The average accuracy of 10 tests is '+str(sum(accuracy_from_tests)/len(accuracy_from_tests)))