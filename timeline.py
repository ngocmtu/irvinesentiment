#!/usr/bin/env python

import pandas as pd 

df = pd.DataFrame(columns=['time','id','favCount','RTCount'])
timelist = []
idlist = []
favlist = []
rtlist = []
with open('cointelegraph','r') as f:
	for each in range(,len(f)):
		f.readline()
		timelist.append(f.readline()[2:])
		idlist.append(f.readline()[4:])
		favlist.append(f.readline()[11:])
		rtlist.append(f.readline()[15:])

df['time'] = timelist
df['id'] = idlist
df['favCount'] = favlist
df['RTCount'] = rtlist 
