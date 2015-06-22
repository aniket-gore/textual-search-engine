"""Module calwts:
    This module reads the input files from tokenization phase,
    calculates tf-idf and stores into output files.
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
    stopwords = defaultdict(int)
    with open("stopwords.txt","r") as stopwords_file:
        for line in stopwords_file:
            stopwords[line.rstrip("\n")] = 1;
    return stopwords

def calculateTermFreqAndInverseDocFreq(input_directory, term_frequency, inverse_document_frequency, term_count_in_corpus):
    stopwords = getstopwordslist()
    # for each input file, build token_freqency. also build inverse_document_frequency simultaneously.
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
    max_count = -1
    max_term = ''
    for term, count in term_dict.iteritems():
        if count > max_count:
            max_count = count
            max_term = term

    return max_term

def calculateWeights(term_weights, term_frequency, inverse_document_frequency, output_directory, term_count_in_corpus):
    # create output_directory if doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    number_of_documents = len(term_frequency)
    # Calculate Normalized Term Frequency
    for filename, term_dict in term_frequency.iteritems():
        with open(os.path.join(output_directory, filename + '_weights'), 'w') as output_file:
            max_frequency_term = findMaxFrequencyTerm(term_dict = term_frequency[filename])
            for term,count in term_frequency[filename].iteritems():
                # Ignore if the term occurs only once in the entire corpus
                if term_count_in_corpus[term] == 1:
                    continue
                term_weights[filename][term] = a + (1 - a) * term_frequency[filename][term] / term_frequency[filename][max_frequency_term]
                term_weights[filename][term] *= math.log(number_of_documents / inverse_document_frequency[term])
                output_file.write(term + '\t' + str(term_weights[filename][term]) + '\n')

def main():
    "This function is the base caller of calcwts for search engine"
    term_frequency = defaultdict(lambda : defaultdict(dict))
    inverse_document_frequency = defaultdict(int)
    term_count_in_corpus = defaultdict(int)
    calculateTermFreqAndInverseDocFreq(input_directory = sys.argv[1], term_frequency = term_frequency, inverse_document_frequency = inverse_document_frequency, term_count_in_corpus = term_count_in_corpus)
    term_weights = defaultdict(lambda : defaultdict(dict))
    calculateWeights(term_weights = term_weights, term_frequency = term_frequency, inverse_document_frequency = inverse_document_frequency, output_directory = sys.argv[2], term_count_in_corpus = term_count_in_corpus)

    print "Running time = %s seconds" %(time.time() - start_time)

if __name__ == "__main__":
    sys.exit(main())
