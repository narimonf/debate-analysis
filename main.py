from debate_type_one import *
from ngram import *
from debate_type_two import *

from pattern.en import parse, Sentence, parse, modality, mood, sentiment, lemma
import ashlib.ling.tokenize
import ashlib.ling.corpus
import ashlib.ling.cnlp
import ashlib.util.stats
import scipy.stats

import math
import os
import sys
import csv
import ntpath
import collections
import csv

"""filepath stuff"""

def read(filePath):
    with open(filePath, "r") as file:
        return file.read()

def hidden(path):
    return path.find(".") == 0

def listStdDir(dirPath):
	std = []
	for name in os.listdir(dirPath):
		 if not hidden(name):
			std.append(os.path.join(dirPath, name))
	return std

""" aggregate stats stuff """

def read_in_all_debates(winning_stats, losing_stats):
	read_in_all_debates_of_type(True, winning_stats, losing_stats)
	read_in_all_debates_of_type(False, winning_stats, losing_stats)

	replace_all_contractions(winning_stats, losing_stats)

def read_in_all_debates_of_type(type1, winning_stats, losing_stats):
	location_of_debates = ''
	if type1: 
		location_of_debates = os.path.dirname(os.path.realpath(__file__)) + '/debates/type1'
	else:
		location_of_debates = os.path.dirname(os.path.realpath(__file__)) + '/debates/type2'
	locations_of_debates = listStdDir(location_of_debates)
	for debate_folder in locations_of_debates:
		locations_of_files_in_debate = listStdDir(debate_folder)
		metadata = ""
		transcript = ""
		for debate_file in locations_of_files_in_debate:
			if debate_file.endswith('metaData.txt'):
				metadata = read(debate_file)
			elif debate_file.endswith('transcript.txt'):
				transcript = read(debate_file)
		debate = object
		if type1:
			debate = DebateTypeOne(metadata, transcript)
		else:
			debate = DebateTypeTwo(metadata, transcript)
		debate.process_debate()
		debate_stats = debate.return_debate_stats()
		add_debate_to_stats(debate_stats, winning_stats, losing_stats)

def add_debate_to_stats(debate_stats, winning_stats, losing_stats):
	winning_stats.sentences += debate_stats.winning_stats.sentences
	winning_stats.motion_words += debate_stats.winning_stats.motion_words
	winning_stats.topic_words += debate_stats.winning_stats.topic_words
	winning_stats.num_applause += debate_stats.winning_stats.num_applause
	winning_stats.num_laughter += debate_stats.winning_stats.num_laughter
	losing_stats.sentences += debate_stats.losing_stats.sentences
	losing_stats.motion_words += debate_stats.losing_stats.motion_words
	losing_stats.topic_words += debate_stats.losing_stats.topic_words
	losing_stats.num_applause += debate_stats.losing_stats.num_applause
	losing_stats.num_laughter += debate_stats.losing_stats.num_laughter


"""ngram stuff"""

CONTRACTIONS = { "n't": " not", "'ve": " have", "'d": " would", "'re": " are", 
				"won't": "will not", "'t": " not", " it's": " it is", " he's": 
				" he is", " she's": " she is" }

def replace_contractions(text):
	for contraction in CONTRACTIONS:
		text = text.replace(contraction, CONTRACTIONS[contraction])
	return text

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

def	audience_reactions(winning_stats, losing_stats):
	calc_and_remove_audience_reactions(winning_stats)
	calc_and_remove_audience_reactions(losing_stats)

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

def write_ngram_to_csv(ngrams, csv_file):
	with csv_file as csvfile:
		fieldnames = ['ngram', 'p_val', 'count1', 'count2']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

		writer.writeheader()
		for ngram_data in ngrams:
			ngram = str(ngram_data.ngram)
			p_val = str(ngram_data.p_val)
			count1 = str(ngram_data.count1)
			count2 = str(ngram_data.count2)
			writer.writerow({'ngram': ngram, 'p_val': p_val, 'count1': count1, 'count2': count2})

	csv_file.close()

def output_all_ngram_data(winning_stats, losing_stats):
	winning_ngrams = open("winning_ngrams.csv", "w")
	write_ngram_to_csv(winning_stats.sig_ngrams, winning_ngrams)
	winning_lemma_ngrams = open("winning_lemma_ngrams.csv", "w")
	write_ngram_to_csv(winning_stats.sig_lemma_ngrams, winning_lemma_ngrams)

	losing_ngrams = open("losing_ngrams.csv", "w")
	write_ngram_to_csv(losing_stats.sig_ngrams, losing_ngrams)
	losing_lemma_ngrams = open("losing_lemma_ngrams.csv", "w")
	write_ngram_to_csv(losing_stats.sig_lemma_ngrams, losing_lemma_ngrams)

def replace_all_contractions(winning_stats, losing_stats):
	for index, sentence in enumerate(winning_stats.sentences):
		winning_stats.sentences[index] = replace_contractions(sentence)
	for index, sentence in enumerate(losing_stats.sentences):
		losing_stats.sentences[index] = replace_contractions(sentence)

def print_lengths(stats, lengths_file, sentence_csv, word_csv):
	lengths_file.write("stats.num_sentences: " + str(stats.num_sentences) + '\n')
	lengths_file.write("stats.avg_sentence_len: " + str(stats.avg_sentence_len) + '\n')
	lengths_file.write("stats.num_words: " + str(stats.num_words) + '\n')
	lengths_file.write("stats.avg_word_len: " + str(stats.avg_word_len) + '\n')
	lengths_file.write("stats.num_chars: " + str(stats.num_chars) + '\n')
	lengths_file.close()

	write_collection_to_csv(stats.sentence_len_distribution, sentence_csv)
	write_collection_to_csv(stats.word_len_distribution, word_csv)

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

def write_collection_to_csv(collection, csv):
	for elem in collection:
		count = collection[elem]
		csv.write(str(elem) + ',' + str(count) + '\n')

	csv.close()

def print_sentiment_analysis(stats, polarity_file, subjectivity_file, mood_file, modality_file):
	write_collection_to_csv(stats.polarity_counts, polarity_file)
	write_collection_to_csv(stats.subjectivity_counts, subjectivity_file)
	write_collection_to_csv(stats.mood_counts, mood_file)
	write_collection_to_csv(stats.modality_counts, modality_file)

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

""" main """

def main():
	winning_stats = AggregateTeamStats()
	losing_stats = AggregateTeamStats()
	
	read_in_all_debates(winning_stats, losing_stats)

	audience_reactions(winning_stats, losing_stats)
	calc_ngram_data(winning_stats, losing_stats)
	calc_lengths(winning_stats, losing_stats)
	sentiment_analysis(winning_stats, losing_stats)

if __name__ == "__main__":
	main()
