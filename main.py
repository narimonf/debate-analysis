from debate_type_one import *
from debate_type_two import *
from calc_data import *

import math
import os
import sys
import csv
import ntpath
import collections

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

""" aggregate stats """

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
