#!/usr/bin/env python

#TODO:
# separate training file data into training and testing sets

import pandas as pd 
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

def cleanTwit(twit):
	filtered_words = []
	for ch in string.punctuation:
		if ch in twit:
			twit = twit.replace(ch,' ')
	wordList = twit.split()
	wordList = [w for w in wordList if w[0] != '$']
	filteredWordList = [w for w in wordList if not w in stop_words]
	for i in range(len(filteredWordList)):
		e = filteredWordList[i].lower()
		if len(e) >= 3:
			filtered_words.append(e)
	return filtered_words

bulltwits = []
beartwits = []
with open(bullfile) as f:
	bulltwits = f.readlines()
with open(bearfile) as f:
	beartwits = f.readlines()

# bullbearlist: simple list with twits with no sentiment
bullbearlist = [cleanTwit(x.strip()) for x in bulltwits] + [cleanTwit(x.strip()) for x in beartwits]
bulltwits = [(cleanTwit(x.strip()),'Bullish') for x in bulltwits]
beartwits = [(cleanTwit(x.strip()),'Bearish') for x in beartwits]

# bullbear: dict of twits and sentiment
bullbear = bulltwits + beartwits
random.shuffle(bullbear)
bullbeartrain = bullbear[:int(len(bullbear)*0.3)]
bullbeartest = bullbear[int(len(bullbear)*0.3):]

def get_words_in_tweets(tweets):
    all_words = []
    for (words, sentiment) in tweets:
    	all_words.extend(words)
    return all_words

def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    word_features = wordlist.keys()
    return word_features

word_features = get_word_features(get_words_in_tweets(bullbeartrain))
print('Word features: ')
print(word_features[0:21])

def extract_features(document):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features

training_set = nltk.classify.apply_features(extract_features, bullbeartrain)
classifier = nltk.NaiveBayesClassifier.train(training_set)
print(classifier.show_most_informative_features(10))

# let model label data in test file
# then cross-check labels with actual test
# fr = pd.read_csv(ofile)
test_set = nltk.classify.apply_features(extract_features, bullbeartest)
print('Accuracy test')
print(nltk.classify.accuracy(classifier,test_set))

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
# percentageCorrect = 'Correct ratio '+str(100*correct/(correct+wrong))+'%'
# print(percentageCorrect)