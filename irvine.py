#!/usr/bin/env python

import pandas as pd 
from datetime import datetime
import pytz
import math
import csv
import sys

ifile = sys.argv[1]
ofile = sys.argv[2]
onan = sys.argv[3]

# Variable definitions
# stockdict: keeps pair stockname-dates it was mentioned
# stocklist: temp list of stocks associated with a twit,
# used to eliminate duplication if twit comes up again
# stocknan: list of twits with delisted stock symbols

f = pd.read_csv(ifile)
stockdict = {}
stocklist = []
stocknan = []
stocknandict = {}
keynan = ''

eastern = pytz.timezone('US/Eastern')

def addDate(symbol, date):
	if symbol not in stocklist:
		date = date.replace(' ', '')
		date = datetime.strptime(date, '%Y-%m-%d%H:%M:%S%Z')
		date = pytz.utc.localize(date)
		date = date.astimezone(eastern)
		date = date.strftime('%d%b%y:%H:%M:%S').upper()
		stocklist.append(symbol)
		if symbol in stockdict:
			stockdict[symbol].append(date)
		else:
			stockdict[symbol] = [date]
		if isinstance(symbol, float) and math.isnan(symbol):
			stocknan.append(keynan)
			stocknandict[keynan] = date

for i in range(len(f)):
	row = f.loc[i,:]
	
	# idxtype: anchor for data; based on how off the value of idxtype is, adjust value
	# of symbol and date accordingly
	idxsym = row.index.get_loc('entities_symbols_symbol')
	idxtime = row.index.get_loc('object_postedTime')
	idxtype = row.index.get_loc('object_objectType')
	keynan = row['none']

	if row[idxtype] == 'note':
		addDate(row[idxsym], row[idxtime])
	elif row[idxtype + 1] == 'note'  :
		addDate(row[idxsym + 1], row[idxtime + 1])
	elif row[idxtype + 2] == 'note' :
		addDate(row[idxsym + 2], row[idxtime + 2])
	elif row[idxtype + 3] == 'note' :
		addDate(row[idxsym + 3], row[idxtime + 3])

	i += 1

	nextRow = ''
	if i < len(f) - 1:
		nextRow = f.loc[i,:]
	else:
		break
	if row['none'] != nextRow['none']:
		stocklist = []

with open(ofile, 'wr') as writeto:
	for k,v in stockdict.items():
		writeto.write(k + ',')
		for each in v[:-1]:
			writeto.write(each + ',')
		writeto.write(v[-1])
		writeto.write('\n')

with open(onan, 'w') as writeto:
	for each in stocknan:
		writeto.write('%s\n' % each)