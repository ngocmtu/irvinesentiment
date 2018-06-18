#!/usr/bin/env python

import sys
from os import path, listdir
import csv

folder = sys.argv[1]
files = listdir(folder)

with open('sentiment_counted','wb') as counted:
	writer = csv.writer(counted)
	for f in files:
		bull_count = 0
		bear_count = 0
		with open(path.join(folder,f),'r') as csvread:
			reader = csv.reader(csvread)
			for row in reader:
				if row[1] > 0.5:
					if row[2] == 'bull':
						bull_count += 1
					if row[2] == 'bear':
						bear_count += 1
		writer.writerow([f,'bull',bull_count,'bear',bear_count])