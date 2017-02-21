from ngram import *
from outputdata import *

from pattern.en import parse, Sentence, parse, modality, mood, sentiment, lemma
import ashlib.ling.tokenize
import ashlib.ling.corpus
import ashlib.ling.cnlp
import ashlib.util.stats
import scipy.stats

import re
import math
import os
import sys
import csv
import ntpath
import collections

def calc_and_remove_audience_reactions(stats):
	applauses = []
	applauses.append("[applause]")
	applauses.append("[APPLAUSE]")

	laughters = []
	laughters.append("[laughter]")
	laughters.append("[LAUGHTER]")

	for index, sentence in enumerate(stats.sentences):
		new_sentence = sentence
		for applause in applauses:
			stats.num_applause += sentence.count(applause)
			new_sentence = new_sentence.replace(applause, '')
		for laughter in laughters:
			stats.num_laughter += sentence.count(laughter)
			new_sentence = new_sentence.replace(laughter, '')

		stats.sentences[index] = new_sentence

def	audience_reactions(winning_stats, losing_stats):
	calc_and_remove_audience_reactions(winning_stats)
	calc_and_remove_audience_reactions(losing_stats)

def lemmatize(sentence):
	words = ashlib.ling.tokenize.words(sentence)

	lemma_words = []

	for word in words:
		lemma_word = lemma(word)
		lemma_words.append(lemma_word)

	lemmatized_sentence = ' '.join(lemma_words)

	#remove space between final word and terminal_punctuation
	length = len(lemmatized_sentence)
	lemmatized_sentence = lemmatized_sentence[:length - 2] + lemmatized_sentence[length - 1:]

	return lemmatized_sentence

def calc_ngram_data(winning_stats, losing_stats):
	winning_stats.ngram_counts = get_team_ngram_counts(winning_stats.sentences)
	losing_stats.ngram_counts = get_team_ngram_counts(losing_stats.sentences)
	winning_stats.sig_ngrams = compare_ngram_counts(winning_stats.ngram_counts, losing_stats.ngram_counts)
	losing_stats.sig_ngrams = compare_ngram_counts(losing_stats.ngram_counts, winning_stats.ngram_counts)

	winning_lemmatized_sentences = []
	losing_lemmatized_sentences = []

	for sentence in winning_stats.sentences:
		lemma_s = lemmatize(sentence)
		winning_lemmatized_sentences.append(lemma_s)
	for sentence in losing_stats.sentences:
		lemma_s = lemmatize(sentence)
		losing_lemmatized_sentences.append(lemma_s)

	winning_stats.lemma_ngram_counts = get_team_ngram_counts(winning_lemmatized_sentences)
	losing_stats.lemma_ngram_counts = get_team_ngram_counts(losing_lemmatized_sentences)
	winning_stats.sig_lemma_ngrams = compare_ngram_counts(winning_stats.lemma_ngram_counts, losing_stats.lemma_ngram_counts)
	losing_stats.sig_lemma_ngrams = compare_ngram_counts(losing_stats.lemma_ngram_counts, winning_stats.lemma_ngram_counts)

	output_all_ngram_data(winning_stats, losing_stats)

def calc_lengths(winning_stats, losing_stats):
	calc_sentence_word_len(winning_stats)
	calc_sentence_word_len(losing_stats)

	winning_lengths = open("winning_lengths.txt", "w")
	losing_lengths = open("losing_lengths.txt", "w")
	winning_sentence_csv = open("winning_sentence_csv.csv", "w")
	winning_word_csv = open("winning_word_csv.csv", "w")
	losing_sentence_csv = open("losing_sentence_csv.csv", "w")
	losing_word_csv = open("losing_word_csv.csv", "w")

	print_lengths(winning_stats, winning_lengths, winning_sentence_csv, winning_word_csv)
	print_lengths(losing_stats, losing_lengths, losing_sentence_csv, losing_word_csv)

def calc_sentence_word_len(stats):
	stats.num_sentences = len(stats.sentences);
	for sentence in stats.sentences:
		wordList = re.sub("[^\w]", " ", sentence).split()
		sentence_len = len(wordList)
		stats.num_words += sentence_len
		stats.sentence_len_distribution[sentence_len] += 1
		for word in wordList:
			word_len = len(word)
			stats.num_chars += word_len
			stats.word_len_distribution[word_len] += 1

	stats.avg_sentence_len = stats.num_words / stats.num_sentences
	stats.avg_word_len = stats.num_chars / stats.num_words

def team_sentiment_analysis(stats):
	for s in stats.sentences:
		this_sentiment = sentiment(s)
		polarity = float("{0:.2f}".format(this_sentiment[0]))
		subjectivity = float("{0:.2f}".format(this_sentiment[1]))
		polarity_10 = float("{0:.1f}".format(this_sentiment[0]))
		subjectivity_10 = float("{0:.1f}".format(this_sentiment[1]))
		stats.polarity_counts[polarity] += 1
		stats.subjectivity_counts[subjectivity] += 1
		stats.polarity_counts_10s[polarity_10] += 1
		stats.subjectivity_counts_10s[subjectivity_10] += 1

		s = Sentence(parse(s, lemmata=True))
		stats.mood_counts[mood(s)] += 1
		rounded_modality = float("{0:.2f}".format(modality(s)))
		rounded_modality_10 = float("{0:.1f}".format(modality(s)))
		stats.modality_counts[rounded_modality] += 1
		stats.modality_counts_10s[rounded_modality_10] += 1


def sentiment_analysis(winning_stats, losing_stats):
	team_sentiment_analysis(winning_stats)
	team_sentiment_analysis(losing_stats)

	win_polarity_file = open("win_polarity.csv", "w")
	win_subjectivity_file = open("win_subjectivity.csv", "w")
	win_mood_file = open("win_mood.csv", "w")
	win_modality_file = open("win_modality.csv", "w")
	lose_polarity_file = open("lose_polarity.csv", "w")
	lose_subjectivity_file = open("lose_subjectivity.csv", "w")
	lose_mood_file = open("lose_mood.csv", "w")
	lose_modality_file = open("lose_modality.csv", "w")

	print_sentiment_analysis(winning_stats, win_polarity_file, 
							 win_subjectivity_file, win_mood_file, win_modality_file)
	print_sentiment_analysis(losing_stats, lose_polarity_file, 
							 lose_subjectivity_file, lose_mood_file, lose_modality_file)
