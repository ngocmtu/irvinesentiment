#!/usr/bin/env python

import csv
import sys
from os import path,listdir,remove

folder = sys.argv[1]
folder_nosen = sys.argv[2]
files_classified = listdir(folder)
files_nosen = listdir(folder_nosen)

twits = []
for f in files_classified:
	classified_pos = f.find('classified')
	nosen_file = f[:classified_pos]+'nosen.csv'
	output_file = f[:f.find('.')] + '_final.csv'
	with open(path.join(folder_nosen,nosen_file),'r') as nosen, open(path.join(folder,f),'r') as classified, open(path.join(folder,output_file),'w') as final:

		classified_reader = csv.reader(classified)
		nosen_reader = csv.reader(nosen)
		writer = csv.writer(final)

		# add twits and their dates to a dictionary
		d = {}
		for row in nosen_reader:
			d[row[1]] = row[0]

		col_name = next(classified_reader)
		col_name.append('created_at')
		writer.writerow(col_name)

		# row is a row in the classified files in list form
		for row in classified_reader:
			twit = row[0]
			row.append(d[twit])
			writer.writerow(row)