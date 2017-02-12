from statsClasses import *

import ashlib.ling.tokenize
import ashlib.ling.corpus
import ashlib.util.stats
import scipy.stats

import math
import os
import sys
import csv
import ntpath
import collections

""" ngram """

def get_team_ngram_counts(sentences):
	MAX_PHRASE_SIZE = 3
	ngram_counts = collections.Counter()

	for sentence in sentences:
		words = ashlib.ling.tokenize.words(sentence)

		for phrase_size in range(1, MAX_PHRASE_SIZE + 1):
			for ngram_index in range(len(words) - phrase_size + 1):
				ngram = tuple(words[word_index] for word_index in range(ngram_index, ngram_index + phrase_size))

				def has_punctuation():
					for word_index in range(len(ngram) - 1):
						if ashlib.ling.corpus.isPunctuation(ngram[word_index]):
							return True
					return False

				if not has_punctuation():
					ngram = ashlib.ling.tokenize.reverse(ngram)
					ngram_counts[ngram] += 1

	return ngram_counts

def compare_ngram_counts(ngram_counts_1, ngram_counts_2):
	sig_ngrams = []

	n1 = 0
	n2 = 0

	for ngram in ngram_counts_1:
		n1 += ngram_counts_1[ngram]
	for ngram in ngram_counts_2:
		n2 += ngram_counts_2[ngram]

	for ngram in ngram_counts_1:
		count_1 = ngram_counts_1[ngram] + 1
		count_2 = ngram_counts_2[ngram] + 1

		if (max(count_1, count_2)) > 10:
			x_bar_1 = float(count_1) / float(n1)
			x_bar_2 = float(count_2) / float(n2)

			s1 = ashlib.util.stats.stdev([1] * count_1 + [0] * (n1 - count_1))
			s2 = ashlib.util.stats.stdev([1] * count_2 + [0] * (n2 - count_2))

			s_delta = math.sqrt((s1 ** 2 / n1) + (s2 ** 2 / n2))

			t = (x_bar_1 - x_bar_2) / s_delta

			df_numerator = math.pow(((s1 ** 2 / n1) + (s2 ** 2 / n2)), 2)
			df_denom_1 = ((s1 ** 2 / n1) ** 2) / (n1 - 1)
			df_denom_2 = ((s2 ** 2 / n2) ** 2) / (n2 - 1)

			df = df_numerator / (df_denom_1 + df_denom_2)

			p_val_1 = scipy.stats.t.cdf(t, df)
			p_val_2 = scipy.stats.t.cdf((x_bar_2 - x_bar_1) / s_delta, df)

			if (p_val_1 >= .975):
				sig_ngrams.append(ngramData(ngram, count_1, count_2, p_val_1))

	return sig_ngrams