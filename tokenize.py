"""Module tokenize:
    This module reads the input files,
    tokenizes them and stores into output files."""
import sys
import time
import glob
import os
from string import maketrans
from bs4 import BeautifulSoup
from collections import defaultdict

start_time = time.time()

def tokenize(html_data, filecount, dictionary, directory):
    "This function tokenizes the given file and stores the tokens into an output file"
    parsedhtml = BeautifulSoup(html_data)
    try:
        output_file_path = "/" + str(filecount) + ".txt";
        output_file_path = os.path.basename(output_file_path)
        output_file = open(os.path.join(directory,output_file_path),'w')
        print "Writing to file="+ output_file_path
    except IOError:
        print "ERROR:[SearchEngine] Unable to open output file in tokenized files directory."
    else:
        text = parsedhtml.get_text()

        for line in text.splitlines():
            line.strip()
            for token in line.split():
                output_token = token.strip(".,[]\"?|!;:-&#'()$^%*+-/<>=_@`\\0123456789").lower()
                output_token = output_token.encode('utf8')
                output_token = ''.join([ c for c in output_token if c not in ('(',')','/','=','[',']','.','"','?','!','_',':',';',',','\'','&','$')])

                if output_token:
                    dictionary[output_token] += 1
                    output_file.write(output_token + '\n')

        output_file.close()

def writeTokenCountsToFile(dictionary):
    "This function writes the total tokens and their counts to an output file"
    try:
        output_file = open(sys.argv[2] + "/tokens.txt",'w')
    except IOError:
        print "ERROR:[SearchEngine] Unable to open output file",output_file
    else:
        for key,value in dictionary.iteritems():
            output_file.write(key + "\t" + str(value) + '\n')
        output_file.close()

def sortByNameAndWriteToFile(dictionary):
    "This function sorts the tokens alphabetically by name into a file"
    try:
        output_file = open(sys.argv[2] + "/sorted_by_name.txt",'w')
    except IOError:
        print "ERROR:[SearchEngine] Unable to open output file",output_file
    else:
        for key,value in sorted(dictionary.items()):
            output_file.write(key + "\t" + str(value) +'\n')
        output_file.close()

def sortByCountAndWriteToFile(dictionary):
    "This function sorts the tokens by count in descendng order into a file"
    try:
        output_file = open(sys.argv[2] + "/sorted_by_count.txt",'w')
    except IOError:
        print "ERROR:[SearchEngine] Unable to open output file",output_file
    else:
        for word in sorted(dictionary, key = dictionary.get, reverse = True):
            output_file.write(word + "\t" + str(dictionary.get(word)) + '\n')
        output_file.close()

def performTokenization():
    "This function reads all the files to generate tokens and writes the output into files"
    filecount = 0
    token_count_dict = defaultdict(int)

    print "parsing input files now:"
    input_directory = sys.argv[1] + "/*.html"
    files = glob.glob(input_directory)

    timingFile = open(sys.argv[2]+"/timingFile.txt",'w')
    timingfilecount = 0
    for filename in files:
        try:
            timingfilecount = timingfilecount + 1
            if timingfilecount % 50 == 0:
                timingFile.write(str(timingfilecount)+'\t'+str(time.time() - start_time)+'\n')
            file = open(filename,'r')
        except IOError:
            print "ERROR:[SearchEngine] Unable to open input file."
        else:
            file_content = file.read()
            filecount += 1
            tokenize(html_data = file_content, filecount = filecount, dictionary = token_count_dict, directory = sys.argv[2])
        finally:
            file.close()
    writeTokenCountsToFile(dictionary = token_count_dict)
    sortByNameAndWriteToFile(dictionary = token_count_dict)
    sortByCountAndWriteToFile(dictionary = token_count_dict)
    timingFile.close()

def main():
    "This function is the base caller of tokenization for search engine"
    performTokenization()
    print "Running time = %s seconds" %(time.time() - start_time)

if __name__ == "__main__":
    sys.exit(main())
