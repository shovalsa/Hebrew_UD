"""
converts lang.mapping format into lang.conllu format.
Please provide the code with a mapping file and the raw.input containing the sentences separated by new line.
Then run:
$ mapping_to_conllu.py path/to/lang.mapping path/to/raw.input

 It is also possible to provide a tokenizer of your own language, which takes a single sentence and returns a list of tokens.
 In such a case, please replace tokenizer = None in line 16 with an appropriate import
"""
import pandas as pd
import csv
import re
import sys
import numpy as np

tokenizer = None

# comment this chunk if run from IDE:
# try:
#     f, mapping_filepath, raw_filepath = sys.argv
# except ValueError:
#     raise Exception("Please provide <path/to/lang.mapping> <path/to/raw.input> as arguments")


# comment this chunk if run from command line:
mapping_filepath = 'he_htb-ud-dev.heblex.mapping'
raw_filepath = 'dev_sentences.txt' # comment this if run from command line



columns = ['line_index', 'ID', 'FORM', 'LEMMA', 'CPOSTAG', 'POSTAG', 'FEATS', 'TOKEN_NO']


def get_raw_sentences():
    raw = open(raw_filepath, 'r')
    return raw.readlines()

def tokenize(sentence, tokenizer=tokenizer):
    """
    Since different languages tokenize sentences differently, this one should be a separate method.
    :param sentence: a standalone sentence (e.g. one line from the raw.input file)
    :param tokenizer: If externally provided, a tokenizer should be such that takes a single sentence as argument
                        and returns a list of tokens.
    :return: a list of tokens
    """
    if tokenizer == None:
        u = re.sub('([!#$%&\()*+,-./:;<=>?@\^_|~])', r' \1 ', sentence)
        u = re.sub('(\s[\'\"`])', r' \1 ', u)
        u = re.sub('([\'`\"]\s)', r' \1 ', u)
        u = re.sub('([\'`\"]$)', r' \1 ', u)
        token_list = re.sub('(^[\'\"`])', r' \1 ', u)
        token_list = re.findall(r"[\w\"]+|[^\w\s]", token_list)
        return token_list
    else:
        return tokenizer(sentence)

def create_df():
    mapping_df = pd.read_csv(mapping_filepath, sep='\t', header=None, quoting=csv.QUOTE_NONE)
    mapping_df.columns = columns
    return mapping_df


def add_sentence(df):
    raw = get_raw_sentences()
    temp_df = []
    first_lemma = df[df['ID'] == 1] #all the rows that start sentences
    indices = first_lemma.index.tolist() # the indices of the above
    for i in range(0, len(indices)):
        try:
            slice = df.iloc[indices[i]:indices[i + 1]] # each 'slice' is the rows that comprise the sentence
        except IndexError:
            slice = df.iloc[indices[i] + 1:] # each 'slice' is the rows that comprise the sentence
        slice = add_tokens(slice, i)
        blank_line = [[' '], [' '], [' '], [' '], [' '], [' '], [' '], [' ']]
        sent_id = [[' '], "# sent_id = {}".format(i+1), [' '], [' '], [' '], [' '], [' '], [' ']]
        sentence = [['_'], "# text = {}".format(raw[i].strip()), [' '], [' '], [' '], [' '], [' '], [' ']]
        temp_df.append(pd.DataFrame(dict(zip(columns, blank_line))))
        temp_df.append(pd.DataFrame(dict(zip(columns, sent_id))))
        temp_df.append(pd.DataFrame(dict(zip(columns, sentence))))
        temp_df.append(slice)
    tmp = pd.concat(temp_df)
    return tmp


def add_tokens(df, i):
    """
    add the full token to the sentence. e.g.
           4   ל
5 ישראל
      becomes
      4-5  לישראל
            4 ל
5 ישראל
    :param df: a df containing the rows of the particular sentence
    :param i: the iterator from the matrix loop (representing the number of sentence)
    :return: a df containing the rows of the particular sentence plus the additional token rows.
    """
    raw = get_raw_sentences()
    rows_list = []
    # rows_list = pd.DataFrame([np.zeros(8)], columns=columns)
    multi_lemma = df[df.duplicated(subset='TOKEN_NO', keep=False)] #returns a full df of the non-standalone lemmas
    for index, row in df.iterrows():
        if (row['line_index'] == multi_lemma['line_index']).any(): #returns true if the line is part of a bigger token (that is, in multi_lemma)
            sentence = tokenize(raw[i], tokenizer)
            token = sentence[row['TOKEN_NO']-1]
            morphemes = multi_lemma[multi_lemma['TOKEN_NO'] == row['TOKEN_NO']] # all the morphemes of the token
            morpheme_indices = morphemes['ID'].tolist()
            token_range = "%d-%d" % (morpheme_indices[0], morpheme_indices[-1]) # something like 15-18
            t = [[' '], token_range, "%s" % token.strip(), ['_'], ['_'], ['_'], ['_'], ['_']]

            range_and_token = pd.DataFrame(dict(zip(columns, t)))  # token range + token
            rows_list.append(range_and_token)
            morpheme = df[df['ID'] == row['ID']]
            rows_list.append(morpheme) # morpheme
            multi_lemma = multi_lemma[multi_lemma['TOKEN_NO'] != row['TOKEN_NO']]
        else:
            rows_list.append(df[df['ID'] == row['ID']]) # standalone lemma
    tmp = pd.concat(rows_list)
    return tmp


def main():
    df = create_df()
    df = add_sentence(df)
    df.drop(columns=['line_index', 'TOKEN_NO'])
    df = df.assign(DEPREL='_')
    df = df.assign(DEPS='_')
    df = df.assign(MISC='_')

    columns = ['ID', 'FORM', 'LEMMA', 'CPOSTAG', 'POSTAG', 'FEATS', 'DEPREL', 'DEPS', 'MISC']
    df.to_csv('fixed_map.conllu', sep='\t', index=False, header=False, quoting=csv.QUOTE_NONE, escapechar='\\', columns=columns)
    print('Successfully converted .mapping to .conllu')
main()
