#!/usr/bin/env python

import pandas as pd 
from datetime import datetime
import pytz
import math
import csv
import sys

ifile = sys.argv[1]
onan = sys.argv[2]

ffull = pd.read_csv(ifile)
f = ffull.loc[:,'object_summary':'provider_link']

sendict = {}
senlist = []
senlistlong = []
keynan = ''

eastern = pytz.timezone('US/Eastern')

def clean(date):
	date = date.replace(' ', '')
	date = datetime.strptime(date, '%Y-%m-%d%H:%M:%S%Z')
	date = pytz.utc.localize(date)
	date = date.astimezone(eastern)
	date = date.strftime('%d%b%y:%H:%M:%S').upper()
	return date

def addDate(symbol, date, sentiment):
	if isinstance(sentiment, float):
		if symbol not in senlist:
			date = clean(date)
			senlist.append(symbol)
			if symbol in senlistlong:
				sendict[symbol][date] = keynan
			else:
				senlistlong.append(symbol)
				sendict[symbol] = {date:keynan}

firstrow = f.loc[0,:]
idxsym = firstrow.index.get_loc('entities_symbols_symbol')
idxtime = firstrow.index.get_loc('object_postedTime')
idxsen = firstrow.index.get_loc('entities_sentiment_basic')
for i in range(len(f)):
	row = f.loc[i,:]
	keynan = row['object_summary']

	addDate(row[idxsym], row[idxtime], row[idxsen])

	if i < len(f) - 1:
		nextRow = f.loc[i + 1,:]
		if row['object_summary'] != nextRow['object_summary']:
			stocklist = []
			senlist = []

with open(onan, 'w') as writeto:
	for each in senlistlong:
		writeto.write(str(each)+', ')
	writeto.write('\n')
	for k,v in sendict.items():
		writeto.write(str(k) + ',')
		for ke, va in v.items():
			writeto.write(ke + ',' + str(va) + ',')
		writeto.write('\n')