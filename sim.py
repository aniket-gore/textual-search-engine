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
import operator

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

def mergeSimilarDocuments(term_weights,merge_string):
    """ Adds a new cluster with weights equal to the average of the two documents in the merge string. Removes the two individual documents"""
    # Get document names from the merge string
    document1 = merge_string.split('_')[0]
    document2 = merge_string.split('_')[1]
    merge_string = merge_string.replace("_","+")

    print merge_string

    term_dict1 = term_weights[document1]
    term_dict2 = term_weights[document2]

    # Add a new cluster with the average of weights of the two documents
    for term,weight in term_dict1.iteritems():
        if term_dict2.has_key(term):
            term_weights[merge_string][term] = (weight + term_dict2[term])/2
        else:
            term_weights[merge_string][term] = weight/2

    for term,weight in term_dict2.iteritems():
        if not term_dict1.has_key(term):
            term_weights[merge_string][term] = weight/2

    # Delete the initial individual documents/clusters
    del term_weights[document1]
    del term_weights[document2]

def findSimilarity(term_weights):
    """ Calculates the similarity scores of all the clusters. Sorts them in the descending order and merges the pair of most similar clusters"""
    document_similarity_scores = defaultdict(float)
    similarity_score = 0
    sum = 0.0
    # Find the similarity scores of all the clusters with all other clusters
    for document1,term_dict1 in term_weights.iteritems():
        for document2,term_dict2 in term_weights.iteritems():
            if document1 == document2:
                continue
            for term,weight in term_dict1.iteritems():
                if term_dict2.has_key(term):
                    similarity_score += weight * term_dict2[term]

            document_similarity_scores[document1 + "_" + document2] = similarity_score
            sum += similarity_score

    median_weight = sum/len(document_similarity_scores)

    min_distance = sys.float_info.max
    document_closest_to_median = ""
    for key in document_similarity_scores:
        temp = math.fabs(document_similarity_scores[key] - median_weight)
        if min_distance > temp:
            document_closest_to_median = key
            min_distance = temp

    print document_closest_to_median


    # Sort the similarity scores in descending order
    sorted_document_similarity_scores = sorted(document_similarity_scores.items(), key=operator.itemgetter(1), reverse=True)

    print "Most similar = ",sorted_document_similarity_scores[0]
    print "Least similar = ",sorted_document_similarity_scores[len(sorted_document_similarity_scores) - 1]


    # Merge the most similar clusters
    mergeSimilarDocuments(term_weights,sorted_document_similarity_scores[0][0])
    return sorted_document_similarity_scores[0][1]


def main():
    "This function is the base caller of calcwts for search engine"
    term_frequency = defaultdict(lambda : defaultdict(dict))
    inverse_document_frequency = defaultdict(int)
    term_count_in_corpus = defaultdict(int)
    calculateTermFreqAndInverseDocFreq(input_directory = sys.argv[1], term_frequency = term_frequency, inverse_document_frequency = inverse_document_frequency, term_count_in_corpus = term_count_in_corpus)
    term_weights = defaultdict(lambda : defaultdict(dict))
    calculateWeights(term_weights = term_weights, term_frequency = term_frequency, inverse_document_frequency = inverse_document_frequency, term_count_in_corpus = term_count_in_corpus)

    number_of_documents = len(term_weights)

    # Perform iterations of merging the most similar clusters till similarity score <= 40% of max score i.e. 527490
    score = 0.0
    for i in range(0,number_of_documents):
        score = findSimilarity(term_weights)
        print i, " -> score= ",score
        if score <= 527490: # 40% of max similarity score
             break

    print "Running time = %s seconds" %(time.time() - start_time)

if __name__ == "__main__":
    sys.exit(main())

