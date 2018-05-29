#!/usr/bin/env python 

import nltk.classify.util, nltk.metrics
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
import itertools
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist

def word_feats(words):
	return dict([(word,True) for word in words])

def evaluate_classifier(featx):
	negids = movie_reviews.fileids('neg')
	posids = movie_reviews.fileids('pos')

	# need full list of words here to get bigrams collocation
	negfeats = [(featx(movie_reviews.words(fileids=[f])),'neg') for f in negids]
	posfeats = [(featx(movie_reviews.words(fileids=[f])),'pos') for f in posids]

	negcutoff = len(negfeats)*4/5
	poscutoff = len(posfeats)*4/5

	trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
	testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]

	classifier = NaiveBayesClassifier.train(trainfeats)
	classifier.show_most_informative_features()

word_fq_pos = FreqDist(movie_reviews.words(categories=['pos']))
word_fq_neg = FreqDist(movie_reviews.words(categories=['neg']))
label_word_fq = ConditionalFreqDist()

for word in movie_reviews.words(categories=['pos']):
	label_word_fq['pos'][word.lower()] += 1

for word in movie_reviews.words(categories=['neg']):
	label_word_fq['neg'][word.lower()] += 1

word_fq = word_fq_neg + word_fq_pos

pos_word_count = label_word_fq['pos'].N()
neg_word_count = label_word_fq['neg'].N()
total_word_count = pos_word_count + neg_word_count
print('Total count: %i, Total pos: %i, Total neg %i' % (total_word_count, pos_word_count, neg_word_count))

word_scores = {}

for word, freq in word_fq.iteritems():
	pos_score = BigramAssocMeasures.chi_sq(label_word_fq['pos'][word], (freq, pos_word_count), total_word_count)
	neg_score = BigramAssocMeasures.chi_sq(label_word_fq['neg'][word], (freq, pos_word_count), total_word_count)
	word_scores[word] = pos_score + neg_score

best = sorted(word_scores.iteritems(), key=lambda (w,s): s, reverse=True)
bestwords = set([w for w,s in best])

def best_word_feats(words):
	return dict([(word, True) for word in words if word in bestwords])

def best_bigram_word_feats(words,score_fn=BigramAssocMeasures.chi_sq,n=200):
	bigram_finder = BigramCollocationFinder.from_words(words)
	bigrams = bigram_finder.nbest(score_fn,n)
	d = dict([(bigram, True) for bigram in bigrams])
	d.update(best_word_feats(words))
	return d

evaluate_classifier(best_bigram_word_feats)

# l = classifier.most_informative_features()
# print('Feature type '+str(type(l[0])))
# for f1,f2 in l[:10]:
# 	print(f1,f2)