#!/usr/bin/env python

# TODO
# there's a long loop somewhere that goes on forever

import sys
import csv
from os import path
import apply_to_folder
import cPickle as pickle 
from itertools import combinations

files = apply_to_folder.get_all_files(sys.argv[1])
ticker_relay_count = {}
ticker_keys = []

# # input
# ticker_list: list of tickers in the same twit
# n: ticker combos (if 2, two tickers in one twit, if 3, 3 tickers in one twit)
# # output
# write to ticker_relay_count
def add_to_ticker_count(ticker_list,n):
	ticker_couple = list(combinations(ticker_list,n)) 
	for couple in ticker_couple:
		if couple in ticker_keys:
			ticker_relay_count[couple] += 1
		else:
			ticker_relay_count[couple] = 1
			ticker_keys.append(couple)

def get_ticker_relationship(f):
	global ticker_relay_count
	global ticker_keys

	time_key_twit_value = {}
	time_keys = set([])

	# if path.isfile('time_key_twit_value.p') and path.isfile('time_keys.p'):
	# 	time_key_twit_value = pickle.load(open('time_key_twit_value.p','r'))
	# 	time_keys = pickle.load(open('time_keys.p','r'))


	# if path.isfile('ticker_relay_count.p') and path.isfile('ticker_keys.p'):
	# 	ticker_relay_count = pickle.load(open('ticker_relay_count.p','r'))
	# 	ticker_keys = pickle.load(open('ticker_keys.p','r'))
	# else:
	with open(f,'r') as csvread:
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

		# pickle.dump(time_key_twit_value,open('time_key_twit_value.p','wb'))
		# pickle.dump(time_keys,open('time_keys.p','wb'))

	for time,ticker_list in time_key_twit_value.iteritems():
		ticker_list = list(set(ticker_list))
		if len(ticker_list) > 1:
			add_to_ticker_count(ticker_list,2)
			add_to_ticker_count(ticker_list,3)

		# pickle.dump(ticker_relay_count,open('ticker_relay_count.p','wb'))
		# pickle.dump(ticker_keys,open('ticker_keys.p','wb'))


	for key, value in sorted(ticker_relay_count.iteritems(), key=lambda (k,v): (v,k)):
		print(str(key) + ': '+str(value))

for f in files:
	get_ticker_relationship(f)