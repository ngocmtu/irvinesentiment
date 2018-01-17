#!/usr/bin/env python

import pandas as pd 
from datetime import datetime
import pytz
import math
import csv
import sys

# TODO
# Add stock to a long list
# Use long list to decide to add to dict or not
# Place the more frequent stocks at top of list

ifile = sys.argv[1]
ofile = sys.argv[2]
onan = sys.argv[3]

# Variable definitions
# stockdict: keeps pair stockname-dates it was mentioned
# stocklist: temp list of stocks associated with a twit,
# used to eliminate duplication if twit comes up again
# stocknan: list of twits with delisted stock symbols

ffull = pd.read_csv(ifile)
f = ffull.loc[:,'object_summary':'provider_link']
stockdict = {}
stocklist = []
stocklistlong = []

sendict = {}
senlist = []
senlistlong = []

stocknan = []
stocknandict = {}
keynan = ''

eastern = pytz.timezone('US/Eastern')

def addDate(symbol, date, sentiment):
	if isinstance(sentiment, float):
		if symbol not in senlist:
			date = date.replace(' ', '')
			date = datetime.strptime(date, '%Y-%m-%d%H:%M:%S%Z')
			date = pytz.utc.localize(date)
			date = date.astimezone(eastern)
			date = date.strftime('%d%b%y:%H:%M:%S').upper()
			senlist.append(symbol)
			if symbol in senlistlong:
				sendict[symbol][date] = keynan
			else:
				senlistlong.append(symbol)
				sendict[symbol] = {date:keynan}
	else:
		if symbol not in stocklist:
			date = date.replace(' ', '')
			date = datetime.strptime(date, '%Y-%m-%d%H:%M:%S%Z')
			date = pytz.utc.localize(date)
			date = date.astimezone(eastern)
			date = date.strftime('%d%b%y:%H:%M:%S').upper()
			stocklist.append(symbol)
			if symbol in stocklistlong:
				stockdict[symbol][date] = sentiment 
			else:
				stocklistlong.append(symbol)
				stockdict[symbol] = {date:sentiment}

	

firstrow = f.loc[0,:]
# idxtype: anchor for data; based on how off the value of idxtype is, adjust value
# of symbol and date accordingly
idxsym = firstrow.index.get_loc('entities_symbols_symbol')
idxtime = firstrow.index.get_loc('object_postedTime')
idxtype = firstrow.index.get_loc('object_objectType')
idxsen = firstrow.index.get_loc('entities_sentiment_basic')
for i in range(len(f)):
	row = f.loc[i,:]
	keynan = row['object_summary']

	if row[idxtype] == 'note':
		addDate(row[idxsym], row[idxtime], row[idxsen])
	elif row[idxtype + 1] == 'note'  :
		addDate(row[idxsym + 1], row[idxtime + 1], row[idxsen + 1])
	elif row[idxtype + 2] == 'note' :
		addDate(row[idxsym + 2], row[idxtime + 2], row[idxsen + 2])
	elif row[idxtype + 3] == 'note' :
		addDate(row[idxsym + 3], row[idxtime + 3], row[idxsen + 3])


	if i < len(f) - 1:
		nextRow = f.loc[i + 1,:]
		if row['object_summary'] != nextRow['object_summary']:
			stocklist = []
			senlist = []

with open(ofile, 'wr') as writeto:
	for each in stocklistlong:
		writeto.write(str(each)+', ')
	for k,v in stockdict.items():
		writeto.write(str(k) + ',')
		for ke, va in v.items():
			writeto.write(ke + ',' + str(va) + ',')
		writeto.write('\n')

with open(onan, 'w') as writeto:
	for each in senlistlong:
		writeto.write(str(each)+', ')
	for k,v in sendict.items():
		writeto.write(str(k) + ',')
		for ke, va in v.items():
			writeto.write(ke + ',' + str(va) + ',')
		writeto.write('\n')