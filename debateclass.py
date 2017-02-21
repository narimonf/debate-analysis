import collections

class DebateStats(object):

	def __init__(self):
		self.magnitude_of_victory = 0
		self.winning_stats = DebateTeamStats()
		self.losing_stats = DebateTeamStats()

class DebateTeamStats(object):
	
	def __init__(self):
		self.sentences = []
		self.motion_words = 0
		self.topic_words = 0
		self.num_applause = 0
		self.num_laughter = 0

class AggregateTeamStats(object):

	def __init__(self):
		self.sentences = []
		self.motion_words = 0
		self.topic_words = 0
		self.ngram_counts = {}
		self.lemma_ngram_counts = {}
		self.sig_ngrams = []
		self.sig_lemma_ngrams = []
		self.num_sentences = 0
		self.avg_sentence_len = 0
		self.sentence_len_distribution = collections.Counter()
		self.num_words = 0
		self.avg_word_len = 0
		self.word_len_distribution = collections.Counter()
		self.num_chars = 0
		self.mood_counts = collections.Counter()
		self.modality_counts = collections.Counter()
		self.polarity_counts = collections.Counter()
		self.subjectivity_counts = collections.Counter()
		self.modality_counts_10s = collections.Counter()
		self.polarity_counts_10s = collections.Counter()
		self.subjectivity_counts_10s = collections.Counter()
		self.num_applause = 0
		self.num_laughter = 0

class ngramData(object):

	def __init__(self, ngram, count1, count2, p_val):
		self.ngram = ngram
		self.count1 = count1
		self.count2 = count2
		self.p_val = p_val
