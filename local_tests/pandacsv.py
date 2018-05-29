#!/usr/bin/env python

import pandas as pd 
# import csv
import sys

fi = sys.argv[1]

df = pd.read_csv(fi)
l = list(df['tweet'])
for each in l:
	each += each

# with open(fi,'r') as f:
# 	reader = csv.reader(f)
# 	for row in reader:
# 		row[1] += row[1]