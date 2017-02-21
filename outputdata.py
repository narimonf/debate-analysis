import csv

CONTRACTIONS = { "n't": " not", "'ve": " have", "'d": " would", "'re": " are", 
				"won't": "will not", "'t": " not", " it's": " it is", " he's": 
				" he is", " she's": " she is" }

def replace_contractions(text):
	for contraction in CONTRACTIONS:
		text = text.replace(contraction, CONTRACTIONS[contraction])
	return text

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
 
