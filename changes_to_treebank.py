import re
import csv
import pandas as pd
import numpy as np

dummy = 'dummy_treebank.csv'
dev_treebank = 'he_htb-ud-dev.conllu'
training_treebank = 'he_htb-ud-train.conllu'

def suit_for_pandas(filepath):
    source = open(filepath, 'r')
    output = open("modified_%s" % filepath, 'w')
    output.write("INDEX	FORM	LEMMA	UPOSTAG	XPOSTAG	FEATS	HEAD	DEPREL	DEPS	MISC\n")
    for line in source.readlines():
        if line[0] == '#':
            output.write('%s\t\t\t\t\t\t\t\t\t\n' % line)
        else:
            output.write(line)

def clean_file(data, filepath):
    source = open('fixed_%s.csv' % filepath, 'r')
    output = open('fixed_%s' % filepath, 'w')


# data = pd.read_csv("modified_%s" % dev_treebank, sep='\t')



def get_elements(data, col_name, value):
    return data[data[col_name] == value]


def get_interaction(data, col_1, value_1, col_2, value_2):
    return data[(data[col_1] == value_1) & (data[col_2] == value_2)]


def naive_change_value(data, column_name, old_value, new_value):
    data.at[data[column_name] == old_value, column_name] = new_value
    return data


def change_COL1xCOL2(data, col1, col2, old_col1_value, old_col2_value, new_col1_value=None, new_col2_value=None):
    if new_col1_value == None:
        data.at[(data[col1] == old_col1_value) & (data[col2] == old_col2_value), col2] = new_col2_value
    else:
        data.at[(data[col1] == old_col1_value) & (data[col2] == old_col2_value), col1] = new_col1_value
    return data


def change_COL1xFEATS(data, col1, feature_value, old_col1_value=None, new_col1_value=None, new_feature_value=None):
    if new_col1_value is not None:
        if old_col1_value is None:
            data.at[data['FEATS'].str.contains(feature_value, na=False), col1] = new_col1_value
        else:
            data.at[(data['FEATS'].str.contains(feature_value, na=False)) & (data[col1] == old_col1_value), col1] = new_col1_value
    elif new_feature_value is not None:
        pass
        # need to find a way to edit a part of a string.
    return data


def get_head(data, dependent):
    """
    :param dependent: can be either a single line or a Series. The output of get_elements() or get_interaction()
    :return: the token which is the head of the given token.
    to further inspect the results of this method, use something like:
        for i, v in dependents.iterrows():
            if get_head(v)['col_1'] == 'some_value':
                print("dependent", v['FORM'])
                print("head", get_head(v)['FORM'])
                print("head", get_head(get_head(v))['FORM'])
    """
    head = dependent
    target_index = int(dependent['HEAD'])
    if target_index == 0:
        return dependent
    else:
        if target_index < int(dependent['INDEX']):
            # 1st int in cell
                while (int(head['INDEX'].split("-")[0]) > target_index):
                    head = data.iloc[int(head.name) - 1]
        elif target_index > int(dependent['INDEX']):
            while int(head['INDEX'].split("-")[0]) < target_index:
                    head = data.iloc[int(head.name) + 1]
    return head


def get_sentences(dataFrame):
    all_sentences = []
    for i, v in dataFrame.iterrows():
        print(type(v))
        sentence = []
        if v['INDEX'] == '1':
            sentence.append(v)




def make_changes(filepath):
    suit_for_pandas(filepath)
    data = pd.read_csv("modified_%s" % filepath, sep='\t')
    data = naive_change_value(data, 'DEPREL', 'iobj', 'obl')
    data = naive_change_value(data, 'DEPREL', 'acl:inf', 'acl')
    data = change_COL1xCOL2(data, 'UPOSTAG', 'DEPREL', 'PRON', 'amod', new_col2_value='det')
    data = change_COL1xFEATS(data, 'DEPREL', 'Prefix=Yes', new_col1_value="compound:affix")
    data = change_COL1xFEATS(data, 'DEPREL', 'VerbType=Cop', old_col1_value='aux', new_col1_value='cop')
    data = naive_change_value(data, 'DEPREL', 'conj:discourse', 'parataxis')
    data = change_COL1xCOL2(data, 'UPOSTAG', 'DEPREL', 'ADV', 'obl:tmod', new_col2_value='advmod')
    data = naive_change_value(data, 'DEPREL', 'advmod:inf', 'acl')
    data = naive_change_value(data, 'DEPREL', 'aux:q', 'mark:q')
    data = naive_change_value(data, 'UPOSTAG', 'PART', 'ADP')
    data = change_COL1xCOL2(data, 'UPOSTAG', 'DEPREL', 'INTJ', 'advmod', new_col2_value='discourse')
    data.to_csv('fixed_%s.csv' % filepath, sep='\t', index=False)

make_changes(dev_treebank)



