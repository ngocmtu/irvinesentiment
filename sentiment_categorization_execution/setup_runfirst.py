#!/usr/bin/env python

# TODO
# ensure all modules are actually installed
# not the current priority

import sys
import subprocess
from os import path, listdir, makedirs

if not path.exists('classified_data'):
	makedirs('classified_data')
if not path.exists('data_to_be_classified'):
	makedirs('data_to_be_classified')
if not path.exists('training_data'):
	makedirs('training_data')

def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

install('nltk')
install('cPickle')