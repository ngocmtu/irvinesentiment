#!/usr/bin/env python

# input: file with tweets and associated probability of either sentiment
# output: same as input but with an extra column of ticker
# used ONLY for classified files without ticker extracted
# the new classify_prod should be able to extract tickers and dates from unclassified files

import sys
import csv
from os import path, listdir, mkdir
from nltk.corpus import stopwords
import cPickle as pickle

top_words=set(stopwords.words('english'))
reload(sys)
sys.setdefaultencoding('utf-8')

# get all files from folder
folder = sys.argv[1]
files = listdir(folder)
output_folder = path.join(folder,'extracted')
if not 'extracted' in files:
	mkdir(output_folder)
else:
	files.remove('extracted')
stock_tickers = [line.rstrip('\n\r') for line in open('tick2015.csv')]
stock_tickers = [tick.lower() for tick in stock_tickers]

for f in files: 
	output_file = f[:-4]+'_extracted.csv'
	output_path = path.join(output_folder,output_file)
	with open(path.join(folder,f),'r') as csvread, open(output_path,'wb') as csvwrite:
		reader = csv.reader(csvread)
		writer = csv.writer(csvwrite)
		writer.writerow(['tweet','probability','sentiment','ticker'])

		for row in reader:
			tweet = unicode(row[0],errors='ignore')
			words = tweet.split()
			tickers = [word for word in words if word[0] == '$' and word[1:].lower() in stock_tickers]
			for ticker in tickers:
				writer.writerow([tweet,row[1],row[2],ticker])