""" Tokenizes a list of files using Python 2.6.
    usage: python tokenize.py <input-dir> <output-dir>
    """

from sys import argv
from os import listdir, makedirs, path
from collections import deque, defaultdict
import re
from time import time

start_time = time()

def tokenize_file(filepath):
    """ This tokenizer splits on non-alphanumeric characters and html tags. It converts all tokens to lower case.
        :type  filepath: str
        :param filepath: path to file to tokenize

        :rtype  dict
        :return {'tokens': list or deque, 'counts': dict or Counter}
        """
    output = {'tokens': deque([]), 'counts': defaultdict(int)}
    with open(filepath, 'r') as open_file:
        for line in open_file:
            line_tokes = re.split(pattern='<.*?>|\W+?', string=line.lower())
                                                            # Regexp split on html tags or non alpha-numeric characters,
                                                            # this is the tokenization step for the line
            line_tokes = list(filter(None, line_tokes))     # hack to remove empty strings
            output['tokens'].extend(line_tokes)             # accumulate these tokens through the entire file
            for tok in line_tokes:                          # update token counts
                output['counts'][tok] += 1
    return output


def tokenize_all_files(input_path, output_path, tokenizer=tokenize_file, num_files=None):
    """ Tokenizes all files in input_path using tokenizer, and saves tokens to file with same name in output_path.
        :type  input_path: str
        :param input_path: path to the input files

        :type  output_path: str
        :param output_path: path to output files

        :type  tokenizer: function
        :param tokenizer: handle to tokenizer
                          return must of the form {'tokens': list or deque, 'counts': dict or Counter}
                          default is tokenize_file

        :type  num_files: int
        :param num_files: an optional number of files to use in input_path, if None, then all files in are used

        :return None
        """
    if not path.exists(output_path):                        # create output directory if doesn't exist
        makedirs(output_path)

    all_tokens = defaultdict(int)

    for filename in listdir(cmd_args['input_dir'])[:num_files]:             # cycle through each file in input directory
        tokenizer_output = tokenizer(input_path + '/' + filename)           # tokenize
        with open(path.join(output_path, filename + '.tokens'), 'w') as open_file:
            open_file.write(', '.join(tokenizer_output['tokens']))          # write tokenized output to file
        open_file.write('\n')
        for token, count in tokenizer_output['counts'].iteritems():
            all_tokens[token] += count                      # accumulate tokens with their frequency/counts
                                                            # write token: frequency lists to file
    write_frequency_file('./token_sorted.txt', sorted(all_tokens.iteritems(), key=lambda x: x[0]))
    write_frequency_file('./frequency_sorted.txt', sorted(all_tokens.iteritems(), key=lambda x: x[1], reverse=True))

    return None


def write_frequency_file(filepath, sorted_list):
    """ Write a file where each line contains a token with its frequency.
        :type  filepath: str
        :param filepath: path to file to write to

        :type  sorted_list: list
        :param sorted_list: list of token, frequency pairs
        """
    with open(filepath, 'w') as open_file:
        open_file.write('Token: Frequency\n'
                        '-----  ---------\n')
        for entry in sorted_list:
            open_file.write(str(entry[0]) + ': ' + str(entry[1]) + '\n')
    return None


def print_table(table):
    """ Pretty print a table provided as a list of rows."""
    col_size = [max(len(str(val)) for val in column) for column in zip(*table)]
    print ('=======================================================================')
    for line in table:
        print ("    ".join("{0:{1}}".format(val, col_size[i]) for i, val in enumerate(line)))
    print ('=======================================================================')
    return None


if __name__ == '__main__':
    cmd_args = {'input_dir': argv[1], 'output_dir': argv[2]}    # parse command line arguments
    tokenize_all_files(input_path=cmd_args['input_dir'], output_path=cmd_args['output_dir'])    # tokenize all files
    print "Running time = %s seconds" %(time() - start_time)
