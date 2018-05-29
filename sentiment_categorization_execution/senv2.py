#!/usr/bin/env python

# Bag-of-words model
# extract all words from given dataset
# extract features and calculate the score of given twit based on individual scores

import sys
import csv
import math
import random
import nltk
from nltk.corpus import stopwords
import string

bullfile = sys.argv[1]
bearfile = sys.argv[2]
reload(sys)
sys.setdefaultencoding('utf-8')

stop_words=set(stopwords.words('english'))

# get rid of all punctuation
# the get rid of words less than 3, stopwords and number
# after initial screening is done (i.e: only words that do not start with $)
def clean_word(word):
	for ch in string.punctuation:
		if ch in word:
			word = word.replace(ch,'')
	if len(word) >= 3 and not word in stop_words and not word.isdigit():
		return word.lower()
	else:
		return None

# split the full twit into a list of words
# clean the list to these criteria
# # no '$' or 'http' in the beginning
# then push these words  
def cleanTwit(twit):
	i = 0
	wordListRaw = twit.split()
	wordList = []
	for each in wordListRaw:
		if each[0] != '$' and each[0:4] != 'http':
			word = clean_word(each)
			wordList.append(word) if not word is None else None
	return wordList

# get the tweet column from the csv file
bulltwits = []
beartwits = []
with open(bullfile,'r') as bu_f,open(bearfile,'r') as be_f:
	bull_reader = csv.reader(bu_f)
	bear_reader = csv.reader(be_f)
	for row in bull_reader:
		bulltwits.append(row[1])
	for row in bear_reader:
		beartwits.append(row[1])

# there's a lot more bull than bear tweets 
# so limit bull data to only equal bear
total_bear_tweets = len(beartwits)
bulltwits = bulltwits[:total_bear_tweets]

# bullbearlist: simple list with twits with no sentiment
bullbearlist = [cleanTwit(x.strip()) for x in bulltwits] + [cleanTwit(x.strip()) for x in beartwits]
bulltwits = [(cleanTwit(x.strip()),'Bullish') for x in bulltwits]
beartwits = [(cleanTwit(x.strip()),'Bearish') for x in beartwits]

# bullbear: dict of twits and sentiment
bullbear = bulltwits + beartwits
random.shuffle(bullbear)

# use k-fold to calculate average accuracy of model
# for i in np.arange(0.0,1.0,0.1):
# 	total_bullbear = len(bullbear)
# 	bullbeartrain = bullbear[0:int(i*total_bullbear)]+bullbear[int((i+0.1)*total_bullbear)]
# 	bullbeartest = bullbear[int(i*total_bullbear):int((i+0.1)*total_bullbear)]

bullbeartrain = bullbear[:int(len(bullbear)*0.8)]
bullbeartest = bullbear[int(len(bullbear)*0.2):]

def get_words_in_tweets(tweets):
    all_words = []
    for (words, sentiment) in tweets:
    	all_words.extend(words)
    return all_words

def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    word_features = dict((key,value) for key,value in wordlist.iteritems() if value>0)
    word_features = word_features.keys()
    return word_features

word_features = get_word_features(get_words_in_tweets(bullbeartrain))

def extract_features(document):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features

# apply_features
# 1st param: name of function to be applied to each token; should return a feature set
# ie: a dict mapping feature names to feature values
# 2nd param: list of tokens to which function should be applied
training_set = nltk.classify.apply_features(extract_features, bullbeartrain)
test_set = nltk.classify.apply_features(extract_features,bullbeartest)

# apply classifier so that only features with a weight > 1.5 gets counted
classifier = nltk.NaiveBayesClassifier.train(training_set)

print('accuracy:'+str(nltk.classify.accuracy(classifier,test_set)))