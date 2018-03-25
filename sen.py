#!/usr/bin/env python

import pandas as pd 
import sys
import csv
import math
import nltk
from nltk.corpus import stopwords
import string

ifile = sys.argv[1] #get labeled data
ofile = sys.argv[2] #holder file
tfile = sys.argv[3] #get tests from test file
resultFile = sys.argv[4] #write result to this file
reload(sys)
sys.setdefaultencoding('utf-8')

stop_words=set(stopwords.words('english'))
bullbear = []
unsen = []
bear = 0
bull = 0
dictcount = 0

f = pd.read_csv(ifile)
ftest = pd.read_csv(tfile)

# this filters out all punctuation in twit body, leaving only words and numbers
# returns single word and sen associated with the word
# WORKING ON: adding bigrams to the mix
#!!!!!!!!!!!!!!!!!!!!!!!!PROBLEM!!!!!!!!!!!!!!!!!!!!!!
#does not return Symbol sign and might treat user name as regular expression
def returnTwitAndSen(tweet,sen):
	filtered_words = []
	for ch in string.punctuation:
		if ch in tweet:
			tweet = tweet.replace(ch,' ')
	tweetList = tweet.split()
	bgrm = list(nltk.bigrams(tweetList)) #bigrams method takes a list 
	filteredTweetList = [w for w in tweetList if not w in stop_words]
	for i in range(len(tweetList)):
		e = tweetList[i].lower()
		if len(e) >= 3:
			filtered_words.append(e)
	bullbear.append((filtered_words,sen))

#this filters out words with punctuation at the end 
# but with the translate method this isn't needed anymore
# if e[-1].isalpha() == False:
# 				if len(e[0:-1]) >= 3: 
# 					e = e[0:-1]
# 					filtered_words.append(e)
# 			else:
# 				filtered_words.append(e)


# get labeled data from ifile
# but this data into dict bullbear
# where 
##### key is twit body
##### value is sentiment
for i in range(len(f)):
	row = f.loc[i,:]
	tweet = row['object_summary']
	sen = row['entities_sentiment_basic']
	if sen == 'Bullish':
		bull += 1
		if bull < 1601:
			returnTwitAndSen(tweet,sen)
			dictcount += 1
	elif sen == 'Bearish':
		bear += 1
		if bear < 1601:
			returnTwitAndSen(tweet,sen)
			dictcount += 1
	# else:
	# 	unsen.append(tweet)

# get test file info and append to third ofile
with open(ofile,'w') as fw:
	fw.write('object_summary,entities_sentiment_basic\n')
	csvwriter = csv.writer(fw,dialect='excel')
	maxtest = 0
	for i in range(len(ftest)):
		row = ftest.loc[i,:]
		sen = row['entities_sentiment_basic']
		if sen == 'Bullish' or sen == 'Bearish':
			maxtest += 1
			if maxtest < 5001 and maxtest%5 == 0:
				tweet = row['object_summary']
				csvwriter.writerow([tweet,sen])

print('Dict count ' + str(dictcount))

def get_words_in_tweets(tweets):
    all_words = []
    for (words, sentiment) in tweets:
    	all_words.extend(words)
    return all_words

def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    word_features = wordlist.keys()
    return word_features

word_features = get_word_features(get_words_in_tweets(bullbear))
print(word_features[0:21])

def extract_features(document):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features

training_set = nltk.classify.apply_features(extract_features, bullbear)
classifier = nltk.NaiveBayesClassifier.train(training_set)
print(classifier.show_most_informative_features(30))

# let model label data in test file
# then cross-check labels with actual test
fr = pd.read_csv(ofile)
with open(resultFile,'w') as fw:
	csvwriter = csv.writer(fw,dialect='excel')
	csvwriter.writerow(['Test chosen every fifth twit'])
	csvwriter.writerow([classifier.most_informative_features(25)])
	correct = 0
	wrong = 0
	for i in range(len(fr)):
		row = fr.loc[i,:]
		tweet = row['object_summary']
		sen = row['entities_sentiment_basic']
		senTest = classifier.classify(extract_features(tweet.split()))
		if sen == senTest:
			correct += 1
			csvwriter.writerow([tweet,sen,senTest,'Correct'])
		else:
			wrong += 1
			csvwriter.writerow([tweet,sen,senTest,'Wrong'])
	print('Correct ' + str(correct))
	print('Wrong ' + str(wrong))
	percentageCorrect = 'Correct ratio '+str(100*correct/(correct+wrong))+'%'
	print(percentageCorrect)
	csvwriter.writerow([percentageCorrect])

#	([unsen[i],classifier.classify(extract_features(each[i].split()))])

# csvwriter.writerow('\''+row['object_summary']+'\''+','+str(row['entities_sentiment_basic'])+'\n')
# print(classifier.show_most_informative_features(35))