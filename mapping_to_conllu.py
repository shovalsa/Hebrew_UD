"""
1. להוריד עמודה של אינדקסים (העמודה הראשונה בmapping)
3.  להשתיל כל משפט raw כהערה לפני העץ הרלוונטי שלו
4. ולהכניס כל טוקן מהמשפט הraw, עם הטווח שלו, לפני המורפמות הרלוונטיות (וזה לפי עמודת מספרי הטוקנים)
2. להוריד עמודה של מספרי טוקנים (העמודה האחרונה ב mapping)
5. אחכ צריך להוסיף 3 עמודות ריקות (כלומר שלוש פעמים  _  ) לכל שורה שמציינת מורפמה.
"""
import pandas as pd
import csv
import re
import numpy as np


mapping_filepath = 'he_htb-ud-dev.heblex.mapping'
raw_filepath = 'dev_sentences.txt'
columns = ['line_index', 'ID', 'FORM', 'LEMMA', 'CPOSTAG', 'POSTAG', 'FEATS', 'TOKEN_NO']


def get_raw_sentences():
    raw = open(raw_filepath, 'r')
    return raw.readlines()


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
        add_tokens(slice, i)
        sentence = [[' '], "# %s" % raw[i].strip(), [' '], [' '], [' '], [' '], [' '], [' ']]
        temp_df.append(pd.DataFrame(dict(zip(columns, sentence))))
        temp_df.append(slice)
        break
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
    # rows_list = pd.DataFrame([np.zeros(8)],columns=columns)
    print(rows_list)
    multi_lemma = df[df.duplicated(subset='TOKEN_NO', keep=False)] #returns a full df of the non-standalone lemmas
    for index, row in df.iterrows():
        if (row['line_index'] == multi_lemma['line_index']).any(): #returns true if the line is part of a bigger token (that is, in multi_lemma)
            sentence = re.sub('\s\"', ' \" ', raw[i])
            sentence = re.sub('\"\s', ' \" ', sentence)
            sentence = re.findall(r"[\w']+|[.,!?;]", sentence)
            token = sentence[row['TOKEN_NO']-1]
            t = [[' '], [' '], " %s" % token.strip(), [' '], [' '], [' '], [' '], [' ']]

            t_df = pd.DataFrame(dict(zip(columns, t)))
            rows_list.append(t_df)
            rows_list.append(row)
            multi_lemma = multi_lemma[multi_lemma['TOKEN_NO'] != row['TOKEN_NO']]
        else:
            rows_list.append(row)
    tmp = pd.concat(rows_list, ignore_index=True)
    print(tmp.head())
    return df


def main():
    df = create_df()
    df = add_sentence(df)
    # df = df.drop(columns=['line_index'])
    # df.to_csv('fixed_map.csv', sep='\t', index=False, header=True, quoting=csv.QUOTE_NONE, escapechar=' ')

main()
