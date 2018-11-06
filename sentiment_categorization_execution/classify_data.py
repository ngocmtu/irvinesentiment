#!/usr/bin/env python

import sys
import csv
from os import path, listdir, mkdir
from nltk.classify import NaiveBayesClassifier
from nltk.tokenize import word_tokenize
import cPickle as pickle
from make_classifier import get_classifier,get_ticker,filter_stock,best_bigram_word_feats

###################################################################
# VARIABLE INITIALIZATIONA
###################################################################

files = listdir('data_to_be_classified')
classifier = get_classifier()
		
###################################################################
# MAIN PROGRAM
###################################################################

while True:
	view_classifier_or_classify = raw_input('Do you want to view information about the classifier or classify new data?(view/new/break) \n')

	if view_classifier_or_classify == 'break':
		print('Thanks for using the program. Goodbye!')
		break
	elif view_classifier_or_classify == 'new':
		print('Classifying files in the data_to_be_classified folder. Classified files will be in the classfied_data folder\n')
		print('How do you want to store ticker information?(one/all)')
		print('(one)One ticker on each row. "$AAPL and $FB bullish" will be stored as two rows, one with $AAPL and other with $FB in ticker column')
		print('(all)All tickers on each row. "$AAPL and $FB bullish" will be stored one row, [$AAPL,$FB] in ticker column')
		ticker_storage = raw_input('Your choice?(one/all) default is one\n')

		if not path.exists('classfied_data'):
			mkdir('classfied_data')

		for f in files:
			classfied_file_name = f+'classified.csv'

			# if there's a 'nosen.csv', gather unclassified data and calculate the probability of it being bull or bear
			# if there's none, move along
			with open(path.join('data_to_be_classified',f),'r') as csvread, open(path.join('classfied_data',classfied_file_name),'wb') as csvwrite:
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
							# get stock tickers from twit
							# get all tickers in one row or each ticker gets a row depending on user's choice
							if ticker_storage == 'all':
								writer.writerow([created_at,line,tickers,probdist.prob(sample),sample])
							else:
								for ticker in tickers:
									writer.writerow([created_at,line,ticker,probdist.prob(sample),sample])
		print('\n')
		print('Classified done')
		print('\n')

	# if user chooses to view information about classifier or no option indicated
	# allow for viewing options
	else:
		classifier_options = raw_input('What would you like to about this classifier?\nShow top features(top)?\nShow custom number of features(custom)?\n')
		if classifier_options == 'top':
			classifier.show_most_informative_features()
		elif classifier_options == 'custom':
			number_of_features = raw_input('How many features do you want to see?\n')
			classifier.show_most_informative_features(n=int(number_of_features))
		else:
			continue
	