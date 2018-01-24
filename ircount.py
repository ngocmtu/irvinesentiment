#!/usr/bin/env python

import pandas as pd 
from datetime import datetime
import pytz
import csv
import sys
import collections

# TODO

ifile = sys.argv[1]
onan = sys.argv[2]

ffull = pd.read_csv(ifile)
f = ffull.loc[:,'object_summary':'provider_link']

stocklistlong = []
stockdict = {}
body = ''

eastern = pytz.timezone('US/Eastern')

def addDate(symbol, date, sentiment):
	date = date.replace(' ', '')
	date = datetime.strptime(date, '%Y-%m-%d%H:%M:%S%Z')
	date = pytz.utc.localize(date)
	date = date.astimezone(eastern)
	symbol = symbol.upper()
	if symbol in stocklistlong:
		stockdict[symbol][date] = sentiment 
	else:
		stocklistlong.append(symbol)
		stockdict[symbol] = {date:sentiment}

firstrow = f.loc[0,:]
idxtime = firstrow.index.get_loc('object_postedTime')
idxsen = firstrow.index.get_loc('entities_sentiment_basic')
idxbody = firstrow.index.get_loc('object_summary')

for i in range(len(f)):
	row = f.loc[i,:]
	if i < len(f) - 1:
		nextRow = f.loc[i + 1,:]
		if row[idxbody] == nextRow[idxbody]:
			continue

	body = row[idxbody]
	createdAt = row[idxtime]
	sentiment = row[idxsen]
	words = body.split()
	for word in words:
		if len(word) > 1 and word[0] == '$':
			word = word.replace(',?!.', '')
			if word[1:].isalpha() == True:
				symbol = word[1:]
				addDate(symbol,createdAt,sentiment)
	
with open(onan, 'w') as f:
	f.write('Stock symbol, Total mentions\n')
	for k,v in sorted(stockdict.items(), key = lambda (k,v): (len(v),k), reverse = True):
		f.write(str(k)+','+str(len(v))+',')
		dayList = []
		for each in v.keys():
			dayList.append(each.date())
		counter = collections.Counter(dayList)
		for day,freq in sorted(counter.items()):
			f.write(day.strftime('%d%b%y')+','+str(freq)+',')
		f.write('\n')

# with open(onan, 'w') as f:
# 	f.write('Stock symbol, Total mentions\n')
# 	for k,v in sorted(stockdict.items(), key = lambda (k,v): (len(v),k), reverse = True):
# 		f.write(str(k)+','+str(len(v))+',')
# 		dayList = []
# 		for each in v.keys():
# 			dayList.append(each.date())
# 		counter = collections.Counter(dayList)
# 		for day,freq in sorted(counter.items(), key = lambda (k,v): (len(v),k), reverse = True):
# 			f.write(day.strftime('%d%b%y')+','+str(freq)+',')
# 		f.write('\n')