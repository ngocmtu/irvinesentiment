#!/usr/bin/env python

# TODO
# add sentiment to the grouping
# find a way to skip every other line: instead of using csv module, split each line


import sys
import csv
import apply_to_folder
import concurrent.futures
import cPickle as pickle 
from itertools import combinations

files = apply_to_folder.get_all_files(sys.argv[1])
ticker_relay_count = {}

# ticker sets are stored in separate lists in one big list
# this is to reduce the time of iterating through the entire big list 
# to look for a ticker combination
# combo-2 is stored in 0, combo-3 in 1 and so on 
ticker_keys_sets = [[],[],[],[],[]]

# # input
# ticker_list: list of tickers in the same twit
# n: ticker combos (if 2, two tickers in one twit, if 3, 3 tickers in one twit)
# # output
# write to ticker_relay_count
def add_to_ticker_count(ticker_list,n):
	global ticker_relay_count
	global ticker_keys_sets

	ticker_couple = list(combinations(ticker_list,n))
	if ticker_couple == []:
		return
	else:
		# (n-2) corresponds to the index in ticker_keys_sets
		ticker_keys = ticker_keys_sets[n-2]
		for couple in ticker_couple:
			if couple in ticker_keys:
				ticker_relay_count[couple] += 1
			else:
				ticker_relay_count[couple] = 1
				ticker_keys_sets[n-2].append(couple)

def get_ticker_relationship(f):
	global ticker_relay_count
	global ticker_keys_sets

	time_key_twit_value = {}
	time_keys = set([])

	# if path.isfile('time_key_twit_value.p') and path.isfile('time_keys.p'):
	# 	time_key_twit_value = pickle.load(open('time_key_twit_value.p','r'))
	# 	time_keys = pickle.load(open('time_keys.p','r'))


	# if path.isfile('ticker_relay_count.p') and path.isfile('ticker_keys_sets.p'):
	# 	ticker_relay_count = pickle.load(open('ticker_relay_count.p','r'))
	# 	ticker_keys_sets = pickle.load(open('ticker_keys_sets.p','r'))
	# else:
	with open(f,'r') as csvread:
		reader = csv.reader(csvread)
		tickers = []
		times = []

		# in order, get from file
		# sentiment, ticker symbol, time
		for line in reader:
			tickers.append(line[3].upper())
			times.append(line[4])

		# use time as key (time_keys)
		# value is the list twit
		for ticker,time in zip(tickers,times):
			if time in time_keys:
				time_key_twit_value[time].append(ticker)
			else:
				time_key_twit_value[time] = [ticker]
				time_keys.add(time)

	max_num_ticker = 1
	for ticker_list in time_key_twit_value.values():
		ticker_list = list(set(ticker_list))
		if len(ticker_list) > max_num_ticker:
			max_num_ticker = len(ticker_list)
			while len(ticker_keys_sets) < max_num_ticker:
				ticker_keys_sets.append([])
		for x in range(2,max_num_ticker):
			add_to_ticker_count(ticker_list,x)

for f in files:
	get_ticker_relationship(f)

with open('test_ticker_relationship.csv','wb') as csvwrite:
	writer = csv.writer(csvwrite)
	for key, value in sorted(ticker_relay_count.iteritems(), key=lambda (k,v): (v,k),reverse=True):
		writer.writerow([key,value])
	print('Finished writing to file')