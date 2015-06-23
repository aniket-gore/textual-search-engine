"""Module retrieve:
    This module calculates the document similarities to the query and returns top 10
    matched documents with the query term weights.
	"""

import sys
import re
import operator
import os
from collections import defaultdict
import glob
import math


def getStopWordsList():
    stopwords = defaultdict(int)
    with open("stopwords.txt","r") as stopwords_file:
        for line in stopwords_file:
            stopwords[line.rstrip("\n")] = 1;
    return stopwords

def preprocessQuery(query):
    "Preprocesses the query by lowercase, removing stopwords"
    # preprocess the query
    preprocessed_query = []
    query_term_weights = []
    query_term_weight = 1
    stopwords_list = getStopWordsList()
    query_term_count = 0
    for term in query:
        term = term.lower()
        query_term_count += 1
        if query_term_count % 2 == 1:
            query_term_weight = float(term)
        # remove stopwords
        elif term and not stopwords_list.has_key(term):
            preprocessed_query.insert(len(preprocessed_query), term)
            query_term_weights.insert(len(query_term_weights), query_term_weight)

    # convert the list into dictionary
    terms_in_query_dict = defaultdict(float)
    index_in_query_term_weights = 0
    for term in preprocessed_query:
        terms_in_query_dict[term] = query_term_weights[index_in_query_term_weights]
        index_in_query_term_weights += 1

    return terms_in_query_dict

def searchInDictionaryFile(query_dict):
    "Gets the term information from dictionary file"
    results_from_dictionary = defaultdict(list)
    with open('dictionary.txt', 'r') as dictionary_file:
        count = 0
        found = 0
        found_term = ""
        for line in dictionary_file:
            count += 1

            if len(query_dict) == 0:
                break

            if found == 1:
                results_from_dictionary[found_term].append(int(line))
                found = 2
                continue

            if found == 2:
                results_from_dictionary[found_term].append(int(line))
                del query_dict[found_term]
                found_term = ""
                found = 0
                continue

            line = line.strip("\n")
            if count % 3 == 1 and query_dict.has_key(line):
                found_term = line
                results_from_dictionary[found_term] = []
                found = 1

        return results_from_dictionary

def calculateDocumentWeights(results_from_dictionary_arg, query_dict):
    "Read the postings file by fseeking to required lines and calculate document-query similarity scores"
    document_query_similarity = defaultdict(float)
    document_term_weights = defaultdict(lambda : defaultdict(dict))

    with open('postings.txt', 'r') as postings_file:
        # read the bytes in one line in postings file, so that we can fseek directly to the required line
        postings_file.seek(0,0)
        postings_line = postings_file.readline()
        bytes_in_one_line = postings_file.tell()
        postings_file.seek(0,0)

        # read the postings file by fseeking to the line and update the dictionaries
        for term,list in results_from_dictionary_arg.iteritems():
            postings_file.seek(0,0)
            # fseek to the required line in postings files
            postings_file.seek(int(results_from_dictionary_arg[term][1] - 1) * bytes_in_one_line)

            # number of lines to read = as specified in the dictionary file
            for loop in range(0,int(results_from_dictionary_arg[term][0])):

                postings_line = postings_file.readline()
                postings_line_tokenized = postings_line.split(",")

                query_term_weight = 0;
                if query_dict.has_key(term):
                    query_term_weight = query_dict[term]

                # cumulative wt. of doc += weight of term * the weight by the query term weight as specified in the query
                if document_query_similarity.has_key(postings_line_tokenized[0]):
                    document_query_similarity[postings_line_tokenized[0]] += float(postings_line_tokenized[1]) * query_term_weight
                else:
                    document_query_similarity[postings_line_tokenized[0]] = float(postings_line_tokenized[1]) * query_term_weight

                # update the dictionary containing the document and term weights of matching terms
                document_term_weights[postings_line_tokenized[0]][term] = float(postings_line_tokenized[1])

    return document_query_similarity, document_term_weights

def retrieveDocuments(query_dict):
    "Retrieves the documents, calculates corresponding weights and displays top 10 results"
    query_dict_local = query_dict.copy()

    results_from_dictionary = searchInDictionaryFile(query_dict_local)
    document_query_similarity, document_term_weights = calculateDocumentWeights(results_from_dictionary,query_dict)

    # sort and display the top 10 results
    sorted_document_query_similarity = sorted(document_query_similarity.items(), key=operator.itemgetter(1), reverse=True)
    for index in range(1,11):
        if index <= len(sorted_document_query_similarity):
            print sorted_document_query_similarity[index-1]


def main():
    "This function is the base caller of retrieve for search engine"
    query_dict = preprocessQuery(query = sys.argv[1:])
    retrieveDocuments(query_dict)

if __name__ == "__main__":
    sys.exit(main())

