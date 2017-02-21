from statsclasses import *

import re
import os
import sys
import nltk
import nltk.tokenize

BAD_CHAR = 'z' * 5

def sentences(text):
	initial = nltk.tokenize.sent_tokenize(text.replace(".\"", "\n").replace(u".\u201D", "\n"))
	sentences = []
	for sentence in initial:
		sentences.append(sentence.replace("\n", " "))
	return sentences

class Debate(object):
	
	def __init__(self, metadata, transcript):
		#args
		self.metadata = metadata
		self.transcript = transcript
		#stats
		self.debate_stats = DebateStats()
		self.winning_lines = []
		self.losing_lines = []
		#speakers
		self.winning_participants = []
		self.losing_participants = []
		self.moderators = []
		#info
		self.motion_words = []
		self.topic_words = []
		#bad lines
		self.pre_process_characters = {}
		self.init_pre_process_characters()
		self.irrelevant_line_indications = []
		self.init_irrelevant_line_indications()
		self.irrelevant_line_indications_reg_express = []
		self.init_irrelevant_line_indications_reg_express()

	def process_debate(self):
		self.parse_metadata()
		self.separate_text_and_data()
		self.process_all_lines_and_data()

	def get_special_words_and_score(self, metadata_lines):
		number_of_relevant_lines = 8
		length = len(metadata_lines)

		#correct for text edit formatting that adds an extra line on some files
		if length == 19:
			length = 18
		elif length == 17:
			length = 16

		curr_line = length - number_of_relevant_lines

		motion_words = metadata_lines[curr_line][len("Motion_Words: "):]
		self.motion_words = motion_words.split(", ")
		curr_line += 1
		topic_words = metadata_lines[curr_line][len("Topic_Keywords: "):]
		self.topic_words = topic_words.split(", ")
		curr_line += 1

		pre_for = int(metadata_lines[curr_line][len("Pre_For: "):])
		curr_line += 1
		pre_against = int(metadata_lines[curr_line][len("Pre_Against: "):])
		curr_line += 2
		post_for = int(metadata_lines[curr_line][len("Post_For: "):])
		curr_line += 1
		post_against = int(metadata_lines[curr_line][len("Post_Against: "):])
		change_for = post_for - pre_for
		change_against = post_against - pre_against
		magnitude_of_victory = abs(change_for - change_against)

		self.debate_stats.magnitude_of_victory = magnitude_of_victory

	def separate_text_and_data(self):
		relevant = False
		winning_team = True
		line_is_name = False

		used_winning_participants = []
		used_losing_participants = []

		spliced_transcript = self.transcript.replace("\r", "").split("\n")

		for line in spliced_transcript:
			line_is_name = False
			line = self.pre_process_line(line)
			for participant in self.winning_participants:
				if participant in line:
					relevant = True
					winning_team = True
					line_is_name = True
			for participant in self.losing_participants:
				if participant in line:
					relevant = True
					winning_team = False
					line_is_name = True
			for moderator in self.moderators:
				if moderator in line:
					relevant = False
					line_is_name = True
			if not line_is_name:
				if self.irrelevant_line(line):
					pass
				elif relevant:
					if winning_team:
						self.winning_lines.append(line)
					else:
						self.losing_lines.append(line)

	def init_pre_process_characters(self):
		self.pre_process_characters.update({"\x92":"'"})

	def pre_process_line(self, line):
		for char in self.pre_process_characters:
			line = re.sub(char, self.pre_process_characters[char], line)

		# new_line = "".join([char if ord(char) < 128 else "z" * 5 for char in line])
		new_line = "".join([char if ord(char) < 128 else BAD_CHAR for char in line])


		return new_line

	def init_irrelevant_line_indications(self):
		self.irrelevant_line_indications.append("Media Transcript")
		self.irrelevant_line_indications.append("Rosenkranz")
		self.irrelevant_line_indications.append("PROGRAM")
		self.irrelevant_line_indications.append("Intelligence Squared")

	def init_irrelevant_line_indications_reg_express(self):
		self.irrelevant_line_indications_reg_express.append("Page \d+")

	def irrelevant_line(self, line):
		for phrase in self.irrelevant_line_indications:
			if phrase in line:
				return True
		
		for phrase in self.irrelevant_line_indications_reg_express:
			instances = re.findall(phrase, line)
			if len(instances) > 0:
				return True

	def process_all_lines_and_data(self):
		self.debate_stats.winning_stats = self.process_team_lines(self.winning_lines)
		self.debate_stats.losing_stats = self.process_team_lines(self.losing_lines)


	def process_team_lines(self, lines):
		text = " ".join(lines)

		num_motion_words = 0
		num_topic_words = 0

		for motion_word in self.motion_words:
			instances = re.findall(motion_word, text)
			num_motion_words += len(instances)
		for topic_word in self.topic_words:
			instances = re.findall(topic_word, text)
			num_topic_words += len(instances)

		all_sentences = sentences(text)

		good_sentences = []

		for sentence in all_sentences:
			# if "z" * 5 not in sentence:
			if BAD_CHAR not in sentence:
				good_sentences.append(sentence)
			#make zs a constant

		team_stats = DebateTeamStats()
		team_stats.sentences = good_sentences
		team_stats.motion_words = num_motion_words
		team_stats.topic_words = num_topic_words

		return team_stats

	def return_debate_stats(self):
		return self.debate_stats




