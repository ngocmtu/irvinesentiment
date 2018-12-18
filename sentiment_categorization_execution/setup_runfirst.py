#!/usr/bin/env python

# TODO
# ensure all modules are actually installed
# not the current priority

import pip
#from os import path, listdir, makedirs

def import_or_install(package):
    try:
        __import__(package)
    except ImportError:
        pip.main(['install', package])

import_or_install('nltk')

# if not path.exists('classified_data'):
# 	makedirs('classified_data')
# if not path.exists('data_to_be_classified'):
# 	makedirs('data_to_be_classified')
# if not path.exists('training_data'):
# 	makedirs('training_data')