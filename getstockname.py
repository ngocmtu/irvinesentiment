#!/usr/bin/env python

import sys
import csv

fsplit = sys.argv[1]
stocks = set([])

def canBeNum(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

#canBeNum(word[1:]) == False

with open(fsplit, 'r') as f:
    for line in f:
    	words = line.split()
    	for word in words:
    		word = word.replace(',', '')
    		if len(word) > 1 and word[0] == '$' and word[1:].isalpha() == True:
    			stocks.add(word[1:])

print(stocks)
