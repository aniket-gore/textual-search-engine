"""Module calwts:
    This module reads the input files from tokenization phase,
    calculates tf-idf and term indices.
	"""

import sys
import time
import os
from collections import defaultdict
import glob
import math

start_time = time.time()

# Maximum tf normalization constant
a = 0.4

def getStopWordsList():
    """ Reads stop words list into memory"""
    stopwords = defaultdict(int)
    with open("stopwords.txt","r") as stopwords_file:
        for line in stopwords_file:
            stopwords[line.rstrip("\n")] = 1;
    return stopwords

def calculateTermFreqAndInverseDocFreq(input_directory, term_frequency, inverse_document_frequency, term_count_in_corpus):
    """ Calculates term frequency and document frequency for all terms in all documents"""
    stopwords = getStopWordsList()
    # For each input file, build token_freqency. Also build inverse_document_frequency simultaneously.
    for input_file in os.listdir(input_directory):
        with open(os.path.join(input_directory, input_file), "r") as filestream:
            # Re-initialize dict tokens_in_file for each file. Used to build inverse_document_frequency
            tokens_in_file = defaultdict(int)
            for line in filestream:
                tokens = line.split(",")
                for token in tokens:
                    # Ignore stopwords
                    token = token.strip()
                    if not token:
                        continue
                    if stopwords.has_key(token):
                        continue
                    # Ignore if token length is 1
                    if len(token) == 1:
                        continue
                    else:
                        # For a particular token, update inverse_document_frequency only on the first occurence of that token in a file
                        if not tokens_in_file.has_key(token):
                            if inverse_document_frequency.has_key(token):
                                inverse_document_frequency[token] += 1
                            else:
                                inverse_document_frequency[token] = 1;
                            tokens_in_file[token] = 1
                        # Update the term_frequency for each token in every file
                        if term_frequency[input_file].has_key(token):
                            term_frequency[input_file][token] += 1
                        else:
                            term_frequency[input_file][token] = 1
                        # Count the term occurence in entire corpus
                        if term_count_in_corpus.has_key(token):
                            term_count_in_corpus[token] += 1
                        else:
                            term_count_in_corpus[token] = 1

def findMaxFrequencyTerm(term_dict):
    """ Returns most frequent term in the given document"""
    max_count = -1
    max_term = ''
    for term, count in term_dict.iteritems():
        if count > max_count:
            max_count = count
            max_term = term

    return max_term

def calculateWeights(term_weights, term_frequency, inverse_document_frequency, term_count_in_corpus):
    """ Calculates term weights for all terms in all documents"""
    number_of_documents = len(term_frequency)
    # Calculate Normalized Term Frequency
    for filename, term_dict in term_frequency.iteritems():
        max_frequency_term = findMaxFrequencyTerm(term_dict = term_frequency[filename])
        for term,count in term_frequency[filename].iteritems():
            # Ignore if the term occurs only once in the entire corpus
            if term_count_in_corpus[term] == 1:
                continue
            term_weights[filename][term] = a + (1 - a) * term_frequency[filename][term] / term_frequency[filename][max_frequency_term]
            term_weights[filename][term] *= math.log(number_of_documents / inverse_document_frequency[term])

def calculateTermIndices(term_weights, term_count_in_corpus, inverse_document_frequency, output_directory):
    """ Finds the term indices of all terms in the corpus and builds the dictionary and postings files"""
    # create output_directory if doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    postingsfile_start_position = 1
    with open(os.path.join(output_directory, 'dictionary.txt'), 'w') as dictionary_file:
        with open(os.path.join(output_directory, 'postings.txt'), 'w') as postings_file:
            for term, count in inverse_document_frequency.iteritems():
                if term_count_in_corpus[term] == 1:
                    continue
                # write to dictionary file by reading term and its occurence in the corpus
                dictionary_file.write(term + '\n' + str(inverse_document_frequency[term]) + '\n' + str(postingsfile_start_position) + '\n')
                postingsfile_start_position += inverse_document_frequency[term]

                # find the term in all the documents and write its weight in postings file
                for filename, term_dict in term_weights.iteritems():
                    if term_dict.has_key(term):
                        postings_file.write(filename + ',' + str(term_dict[term]) + '\n')


def main():
    "This function is the base caller of calcwts for search engine"
    term_frequency = defaultdict(lambda : defaultdict(dict))
    inverse_document_frequency = defaultdict(int)
    term_count_in_corpus = defaultdict(int)
    calculateTermFreqAndInverseDocFreq(input_directory = sys.argv[1], term_frequency = term_frequency, inverse_document_frequency = inverse_document_frequency, term_count_in_corpus = term_count_in_corpus)
    term_weights = defaultdict(lambda : defaultdict(dict))
    calculateWeights(term_weights = term_weights, term_frequency = term_frequency, inverse_document_frequency = inverse_document_frequency, term_count_in_corpus = term_count_in_corpus)


    calculateTermIndices(term_weights = term_weights, term_count_in_corpus = term_count_in_corpus, inverse_document_frequency = inverse_document_frequency, output_directory = sys.argv[2])
    print "Running time = %s seconds" %(time.time() - start_time)

if __name__ == "__main__":
    sys.exit(main())

