import re
import csv
import pandas as pd
import numpy as np
from collections import Counter
import re

dummy = 'dummy_treebank.csv'
dev_treebank = 'he_htb-ud-dev.conllu'
training_treebank = 'he_htb-ud-train.conllu'
test_treebank = 'he_htb-ud-test.conllu'


def suit_for_pandas(filepath):
    source = open(filepath, 'r')
    output = open("modified_%s" % filepath, 'w')
    output.write("INDEX	FORM	LEMMA	UPOSTAG	XPOSTAG	FEATS	HEAD	DEPREL	DEPS	MISC\n")
    sent_id = ''
    for line in source.readlines():
        if 'sent_id' in line:
            sent_id = "".join([x for x in line if x.isnumeric()])
        if line[0] == '#':
            output.write('%s\t\t\t\t\t\t\t\t\t\n' % line)
        else:
            output.write(line)




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

def get_context(data, dependent):
    """
    shows the head and the sentence of the given dependent
    :param data:
    :param dependent:
    :return:
    """
    sentence = dependent
    while '#' not in str(sentence['INDEX']):
        sentence = data.iloc[int(sentence.name) - 1]
    context = [dependent, get_head(data, dependent), sentence['INDEX']]
    return context


def change_dependent(data, extract_col, extract_value, old_dependent_rel, new_dependent_rel, head_rel):
    name = 0
    advs = get_elements(data, extract_col, extract_value)
    for i, v in advs.iterrows():
        if (get_head(data, v)['DEPREL'] == head_rel) and (v['DEPREL'] == old_dependent_rel):
            data.at[v.name, 'DEPREL'] = new_dependent_rel
    return data




def flip_aux_xcomp_for_modals(data):

    deps = get_elements(data, 'DEPREL', 'xcomp')
    for i, v in deps.iterrows():
        head = get_head(data, v)
        if 'VerbType=Mod' in head['FEATS']:
            deps.loc[i, 'DEPREL'] = head['DEPREL']
            data.loc[head.name, 'DEPREL'] = 'aux'
            data.loc[i, 'DEPREL'] = deps.loc[i, 'DEPREL']

            deps.loc[i, 'HEAD'] = head['HEAD']
            data.loc[head.name, 'HEAD'] = v['INDEX']
            data.loc[i, 'HEAD'] = deps.loc[i, 'HEAD']

            # v['HEAD'] = head['HEAD']
            # head['HEAD'] = v['INDEX']
    return data


def make_changes(filepath):
    suit_for_pandas(filepath)
    data = pd.read_csv("modified_%s" % filepath, sep='\t', quoting=csv.QUOTE_NONE)
    # data.columns = ["SENTENCE", "INDEX", "FORM", "LEMMA", "UPOSTAG", "XPOSTAG", "FEATS", "HEAD", "DEPREL", "DEPS", "MISC"]
    data = naive_change_value(data, 'DEPREL', 'iobj', 'obl')
    data = naive_change_value(data, 'DEPREL', 'acl:inf', 'acl')
    data = naive_change_value(data, 'DEPREL', 'det:quant', 'det')
    data = change_COL1xCOL2(data, 'UPOSTAG', 'DEPREL', 'PRON', 'amod', new_col2_value='det')
    data = change_COL1xCOL2(data, 'XPOSTAG', 'DEPREL', 'PRON', 'amod', new_col2_value='det')
    data = change_COL1xFEATS(data, 'DEPREL', 'Prefix=Yes', new_col1_value="compound:affix")
    data = change_COL1xFEATS(data, 'DEPREL', 'VerbType=Cop', old_col1_value='aux', new_col1_value='cop')
    data = naive_change_value(data, 'DEPREL', 'conj:discourse', 'parataxis')
    data = change_COL1xCOL2(data, 'UPOSTAG', 'DEPREL', 'ADV', 'obl:tmod', new_col2_value='advmod')
    data = change_COL1xCOL2(data, 'XPOSTAG', 'DEPREL', 'ADV', 'obl:tmod', new_col2_value='advmod')
    data = naive_change_value(data, 'DEPREL', 'advmod:inf', 'acl')
    data = naive_change_value(data, 'DEPREL', 'aux:q', 'mark:q')
    data = naive_change_value(data, 'UPOSTAG', 'PART', 'ADP')
    data = naive_change_value(data, 'XPOSTAG', 'PART', 'ADP')
    data = change_COL1xCOL2(data, 'UPOSTAG', 'DEPREL', 'INTJ', 'advmod', new_col2_value='discourse')
    data = change_COL1xCOL2(data, 'XPOSTAG', 'DEPREL', 'INTJ', 'advmod', new_col2_value='discourse')
    data = change_dependent(data, 'UPOSTAG', 'ADV', 'dep', 'advmod', 'advmod:phrase')
    data = flip_aux_xcomp_for_modals(data)
    data.to_csv('fixed_%s' % filepath, sep='\t', index=False, header=False, quoting=csv.QUOTE_NONE)

make_changes(training_treebank)

def inspect(data, dataSeries):
    postags = []
    relevant_heads = []
    for i, v in dataSeries.iterrows():
        context = get_context(data, v)
        dependent = context[0]
        head = context[1]
        sentence = context[2]
        if (dependent['UPOSTAG'] == 'ADV') and (head['DEPREL'] == 'advmod:phrase'):
            relevant_heads.append(head['DEPREL'])
            print(sentence)
            print(dependent['INDEX'], dependent['FORM'], dependent['UPOSTAG'])
            print(head['INDEX'], head['FORM'], head['UPOSTAG'])
        postags.append(dependent['UPOSTAG'])

    print(Counter(relevant_heads))
    print(Counter(postags))

    # if get_head(v)['col_1'] == 'some_value':
    #     print("dependent", v['FORM'])
    #     print("head", get_head(v)['FORM'])
    #     print("head", get_head(get_head(v))['FORM'])


