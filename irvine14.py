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
stocklistlong = []

sendict = {}
senlistlong = []

stocknan = []
stocknandict = {}
keynan = ''

eastern = pytz.timezone('US/Eastern')

def addDate(symbol, date, sentiment):
	if isinstance(sentiment, float):
		date = date.replace(' ', '')
		date = datetime.strptime(date, '%Y-%m-%d%H:%M:%S%Z')
		date = pytz.utc.localize(date)
		date = date.astimezone(eastern)
		date = date.strftime('%d%b%y:%H:%M:%S').upper()
		if symbol in senlistlong:
			sendict[symbol][date] = keynan
		else:
			senlistlong.append(symbol)
			sendict[symbol] = {date:keynan}
	else:
		date = date.replace(' ', '')
		date = datetime.strptime(date, '%Y-%m-%d%H:%M:%S%Z')
		date = pytz.utc.localize(date)
		date = date.astimezone(eastern)
		date = date.strftime('%d%b%y:%H:%M:%S').upper()
		if symbol in stocklistlong:
			stockdict[symbol][date] = sentiment 
		else:
			stocklistlong.append(symbol)
			stockdict[symbol] = {date:sentiment}

firstrow = f.loc[0,:]
idxbody = firstrow.index.get_loc('object_summary')
idxtime = firstrow.index.get_loc('object_postedTime')
idxtype = firstrow.index.get_loc('object_objectType')
idxsen = firstrow.index.get_loc('entities_sentiment_basic')

for i in range(len(f)):
	row = f.loc[i,:]
	if i < len(f) - 1:
		nextRow = f.loc[i + 1,:]
		if row[idxbody] == nextRow[idxbody]:
			continue

	keynan = row[idxbody]
	createdAt = row[idxtime]
	sentiment = row[idxsen]
	words = keynan.split()
	for word in words:
		if len(word) > 1 and word[0] == '$':
			word = word.replace(',?!.', '')
			if word[1:].isalpha() == True:
				symbol = word[1:].upper()
				addDate(symbol,createdAt,sentiment)

with open(ofile, 'wr') as writeto:
	for k,v in stockdict.items():
		writeto.write(str(k) + ',')
		for ke, va in v.items():
			writeto.write(ke + ',' + str(va) + ',')
		writeto.write('\n')

with open(onan, 'w') as writeto:
	for k,v in sendict.items():
		writeto.write(str(k) + ',')
		for ke, va in v.items():
			writeto.write(ke + ',' + str(va) + ',')
		writeto.write('\n')