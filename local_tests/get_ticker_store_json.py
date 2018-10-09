#!/usr/bin/env python

import sys, csv
import apply_to_folder

files = apply_to_folder.get_all_files(sys.argv[1])

def get_ticker(tweet):
	words = tweet.split()
	return [word.upper() for word in words if word[0] == '$' and word[1:].isalpha() == True]

all_twits = []
for f in files:
	f_write = f[:-4] + '_ticker.csv'
	with open(f,'r') as csvread, open(f_write,'wb') as csvwrite:
		reader = csv.reader(csvread)
		writer = csv.writer(csvwrite)
		for line in reader:
			twit = line[0] + line[2]
			if twit not in all_twits:
				tickers = get_ticker(twit)
				writer.writerow([line[0],tickers,line[1],line[2],line[4]])
				all_twits.append(twit)