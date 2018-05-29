#!/usr/bin/env python

import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from nltk.collocations import BigramCollocationFinder, BigramAssocMeasures
from nltk.tokenize import word_tokenize
from nltk import bigrams 
from nltk import FreqDist
import sys
from nltk.corpus import stopwords

stop_words=set(stopwords.words('english'))
reload(sys)
sys.setdefaultencoding('utf-8')
 
def word_feats(words):
    return dict([(word, True) for word in words])
 
bull = sys.argv[1]
bear = sys.argv[2]

def best_bigram_word_feats(words,score_fn=BigramAssocMeasures.chi_sq,n=1000):
	bigram_finder = BigramCollocationFinder.from_words(words)
	bigram_finder.apply_word_filter(lambda w: not w.isalpha())
	bigram_finder.apply_word_filter(lambda w: w in stop_words)
	bigram_finder.apply_word_filter(lambda w: len(w)<3)
	bigram_finder.apply_word_filter(lambda w: w[0]=='$')

	bigrams = bigram_finder.nbest(score_fn,n)
	d = dict([(bigram, True) for bigram in bigrams])

	single_words = [word.lower() for word in words if len(word) > 3 and not word[0] == '$']
	d.update(word_feats(single_words))
	return d

with open(bull) as bull_f, open(bear) as bear_f:
	# bullfeats = [(word_feats(line),'bull') for line in fr.readlines()]
	bull_lines = bull_f.readlines()
	bear_lines = bear_f.readlines()
	bull_words = []
	bear_words = []
	# for line in lines:
	# 	toks = word_tokenize(line)
	# 	words += [tok for tok in toks if not tok in stop_words]
	for line in bull_lines:
		line = unicode(line,errors='ignore')
		bull_words.append(word_tokenize(line))
	for line in bear_lines:
		line = unicode(line,errors='ignore')
		bear_words.append(word_tokenize(line))

	# BigramCollocationFinder.from_words takes param of list of words
	bull_feats = [(best_bigram_word_feats(bull_word),'bull') for bull_word in bull_words]
	bear_feats = [(best_bigram_word_feats(bear_word),'bear') for bear_word in bear_words]

	bull_cutoff = len(bull_feats)*5/6
	bear_cutoff = len(bear_feats)*5/6

	trainfeats = bull_feats[:bull_cutoff] + bear_feats[:bear_cutoff]
	testfeats = bull_feats[bull_cutoff:] + bear_feats[bear_cutoff:]

	classifier = NaiveBayesClassifier.train(trainfeats)
	classifier.show_most_informative_features(20)

	print 'accuracy:', nltk.classify.util.accuracy(classifier, testfeats)
	# score = sorted(finder.score_ngrams(bigram_measures.raw_freq), key=lambda x: x[1], reverse = True)
	# for bi,s in score[:10]:
	# 	print(bi,s)
	# print(str(len(finder.score_ngrams(bigram_measures.raw_freq))))
	# print(finder.nbest(bigram_measures.pmi, 20))



# negids = movie_reviews.fileids('neg')
# posids = movie_reviews.fileids('pos')
 
# negfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
# posfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'pos') for f in posids]
# negcutoff = len(negfeats)*3/4
# poscutoff = len(posfeats)*3/4
 
# trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
# testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]
# print 'train on %d instances, test on %d instances' % (len(trainfeats), len(testfeats))
 
# classifier = NaiveBayesClassifier.train(trainfeats)

# classifier.show_most_informative_features()