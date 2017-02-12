from debateClass import *

class DebateTypeTwo(Debate):

	def __init__(self, metadata, transcript):
		super(DebateTypeTwo, self).__init__(metadata, transcript)

	"""parse metadata"""

	def parse_metadata(self):
		metadata_lines = self.metadata.replace("\r", "").split("\n")

		self.get_moderators(metadata_lines)
		self.get_participants(metadata_lines)
		self.get_special_words_and_score(metadata_lines)


	def get_moderators(self, metadata_lines):
		moderator = "Robert Rosenkranz:"
		self.moderators.append(moderator)
		moderator = "Donna Wolfe:"
		self.moderators.append(moderator)
		moderator = "Audience Member:"
		self.moderators.append(moderator)

		moderator_defintion = "Moderator: "
		mod_def_len = len(moderator_defintion)
		index_of_moderator = 1
		moderator = metadata_lines[index_of_moderator][mod_def_len:]
		moderator = moderator + ":"
		self.moderators.append(moderator)

	def get_participants(self, metadata_lines):
		team1 = []
		team2 = []

		len_participant_declaration = len("Team1_Participant1: ")

		for line in metadata_lines:
			if "Winning_Team" in line: # happens last
				if "Team1" in line:
					self.winning_participants = team1
					self.losing_participants = team2
				elif "Team2" in line:
					self.winning_participants = team2
					self.losing_participants = team1
			elif "Team1" in line:
				participant = line[len_participant_declaration:]
				participant = participant + ":"
				team1.append(participant)
			elif "Team2" in line:
				participant = line[len_participant_declaration:]
				participant = participant + ":"
				team2.append(participant)

