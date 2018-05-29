#!/usr/bin/env python

# Extension of senv2.py
# Added bigram collocation score

import pandas as pd 
import sys
import csv
import math
import random
import nltk
from nltk.corpus import stopwords
import string
from nltk.tokenize import word_tokenize

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
	wordListRaw = twit.split()
	wordList = []
	for each in wordListRaw:
		if each[0] != '$' and each[0:4] != 'http':
			word = clean_word(each)
			wordList.append(word) if not word is None else None
	return wordList

bulltwits = []
beartwits = []
with open(bullfile) as f:
	bulltwits = f.readlines()
with open(bearfile) as f:
	beartwits = f.readlines()

# get all words in tweets to calculate bigram measures
# this is exclusively done to get bigrams so that we clean bigrams before doing 
# any calculations
# Return: a list of words
def get_all_words_in_tweets(tweets):
	all_words = []
	for tweet in tweets:
		all_words += word_tokenize(tweet)
	return all_words

all_bull_words = get_all_words_in_tweets(bulltwits)
all_bear_words = get_all_words_in_tweets(beartwits)
all_bullbear_words = all_bear_words + all_bull_words

finder = nltk.BigramCollocationFinder.from_words(all_bullbear_words)
bigram_measures = nltk.BigramAssocMeasures()
finder.apply_word_filter(lambda w: not w.isalpha())
finder.apply_word_filter(lambda w: w in stop_words)
finder.apply_word_filter(lambda w: len(w)<3)
score = sorted(finder.score_ngrams(bigram_measures.raw_freq), key=lambda x: x[1], reverse = True)
for bi,s in score[:10]:
	print(bi,s)




# bullbearlist: simple list with twits with no sentiment
bullbearlist = [cleanTwit(x.strip()) for x in bulltwits] + [cleanTwit(x.strip()) for x in beartwits]
bulltwits = [(cleanTwit(x.strip()),'Bullish') for x in bulltwits]
beartwits = [(cleanTwit(x.strip()),'Bearish') for x in beartwits]

# bullbear: dict of twits and sentiment
bullbear = bulltwits + beartwits
random.shuffle(bullbear)
bullbeartrain = bullbear[:int(len(bullbear)*0.5)]
bullbeartest = bullbear[int(len(bullbear)*0.3):]

# def get_words_in_tweets(tweets):
#     all_words = []
#     for (words, sentiment) in tweets:
#     	all_words.extend(words)
#     return all_words

# def get_word_features(wordlist):
#     wordlist = nltk.FreqDist(wordlist)
#     word_features = dict((key,value) for key,value in wordlist.iteritems() if value>0)
#     word_features = word_features.keys()
#     return word_features

# word_features = get_word_features(get_words_in_tweets(bullbeartrain))

# def extract_features(document):
#     document_words = set(document)
#     features = {}
#     for word in word_features:
#         features['contains(%s)' % word] = (word in document_words)
#     return features

# # apply_features
# # 1st param: name of function to be applied to each token; should return a feature set
# # ie: a dict mapping feature names to feature values
# # 2nd param: list of tokens to which function should be applied
# training_set = nltk.classify.apply_features(extract_features, bullbeartrain)
# print(type(training_set))
# print("Length of training_set "+str(len(training_set)))

# # apply classifier so that only features with a weight > 1.5 gets counted
# classifier = nltk.NaiveBayesClassifier.train(training_set)
# feature_set = classifier.most_informative_features(10)
# print('Feature set type '+str(type(feature_set)))
# for word,feature in feature_set:
# 	print(word)
# 	print(feature)

# print(classifier.show_most_informative_features(10))

# let model label data in test file
# then cross-check labels with actual test
# fr = pd.read_csv(ofile)
# test_set = nltk.classify.apply_features(extract_features, bullbeartest)
#print(test_set[0])
#print(nltk.classify.accuracy(classifier,test_set))

# testtwits = list(bullbeartest.keys())
# correct = 0
# wrong = 0
# for i in range(len(testtwits)):
# 	senTest = classifier.classify(extract_features(tweet.split()))
# 	if sen == senTest:
# 		correct += 1
# 		csvwriter.writerow([tweet,sen,senTest,'Correct'])
# 	else:
# 		wrong += 1
# 		csvwriter.writerow([tweet,sen,senTest,'Wrong'])
# print('Correct ' + str(correct))
# print('Wrong ' + str(wrong))

# print(percentageCorrect)