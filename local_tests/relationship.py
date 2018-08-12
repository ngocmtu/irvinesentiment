#!/usr/bin/env python

import sys
import csv
from os import path
import apply_to_folder
import cPickle as pickle 
from itertools import combinations

files = apply_to_folder.get_all_files(sys.argv[1])
ticker_relay_count = {}
		ticker_keys = []

def get_ticker_relationship(f):
	global ticker_relay_count
	global ticker_keys
	with open(f,'r') as csvread:
		time_key_twit_value = {}
		time_keys = set([])
		reader = csv.reader(csvread)
		tickers = []
		times = []

		# 1st way
		for line in reader:
			tickers.append(line[3].upper())
			times.append(line[4])

		for ticker,time in zip(tickers,times):
			if time in time_keys:
				time_key_twit_value[time].append(ticker)
			else:
				time_key_twit_value[time] = [ticker]
				time_keys.add(time)

		for time,ticker_list in time_key_twit_value.iteritems():
			ticker_list = list(set(ticker_list))
			if len(ticker_list) > 1:
				ticker_couple = list(combinations(ticker_list,2)) 
				for couple in ticker_couple:
					if couple in ticker_keys:
						ticker_relay_count[couple] += 1
					else:
						ticker_relay_count[couple] = 1
						ticker_keys.append(couple)

	for key, value in sorted(ticker_relay_count.iteritems(), key=lambda (k,v): (v,k)):
		print(str(key) + ': '+str(value))

for f in files:
	get_ticker_relationship(f)