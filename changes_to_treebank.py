import re
import csv
import pandas as pd
import numpy as np
from collections import Counter
import re

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
            output.write('\n')
        if line[0] == '#':
            output.write(line + "\t"*9 + '\n')
        elif line.strip() != '':
            # output.write(sent_id + ',' + line)
            output.write(line)

def add_sentence(data):
    data = data.assign(SENTENCE='_')
    data['SENTENCE'] = data['INDEX'].str.split(',').str[0]
    data['INDEX'] = data['INDEX'].str.split(',').str[1]
    return data


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
    context = [dependent['FORM'], sentence['INDEX']]
    return context





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
    return data

def change_dependent(data, extract_col, extract_value, col, old_dependent_value, new_dependent_value, head_value):
    name = 0
    advs = get_elements(data, extract_col, extract_value)
    for i, v in advs.iterrows():
        if (get_head(data, v)[col] == head_value) and (v[col] == old_dependent_value):
            data.at[v.name, col] = new_dependent_value
    return data

def predicative_complements_to_xcomp(data):
    """
    UD guidelines tag predicative complemets as xcomp.
    examples:
    you look great - 'look' is root and 'great' is xcomp
    we expected them to change their minds - expected is root, them is obj (on expected) and change is xcomp (on expected)

    update: changing the latter case is super specific and also more complicated (as the verb is the head of the head and
    it's impossible to validate the intermediate noun), so for the moment it is aborted.
    :param data:
    :return:
    """
    adjs = get_elements(data, 'UPOSTAG', 'ADJ')
    for index, v in adjs.iterrows():
        if get_head(data, v)['UPOSTAG'] == 'VERB' and v['DEPREL'] in ['advcl', 'advmod']:
            data.at[v.name, 'DEPREL'] = 'xcomp'
    # verbs = get_elements(data, 'UPOSTAG', 'VERB')
    # for index, v in verbs.iterrows():
    #     if v['DEPREL'] == 'acl':
    #         head = get_head(data, v)
    #         head_of_head = get_head(data, head)
    #         if head_of_head['UPOSTAG'] == 'VERB' and head['DEPREL'] == 'obj' and head['UPOSTAG'] == 'PRON':
    #             print(get_context(data, v))
    #             print(head_of_head['FORM'])
    #             print(v['FORM'], v['DEPREL'])

    return data

def advmod_phrase_to_fixed(data):
    """
    In case of advmod:phrase, make its dependent's relation 'fixed' instead of advmod or dep
    :param data:
    :return:
    """
    advmods = get_elements(data, 'DEPREL', 'advmod')
    deps = get_elements(data, 'DEPREL', 'dep')
    for i, v in advmods.iterrows():
        if get_head(data, v)['DEPREL'] == 'advmod:phrase':
            data.at[v.name, 'DEPREL'] = 'fixed'
    for i, v in deps.iterrows():
        if get_head(data, v)['DEPREL'] == 'advmod:phrase':
            data.at[v.name, 'DEPREL'] = 'fixed'
    return data

def inspect(data):
    roots = get_elements(data, 'DEPREL', 'root')
    for i, v in roots.iterrows():
        print(get_head(data, v)['FORM'], " ", v['FORM'])

def make_changes(filepath):
    suit_for_pandas(filepath)
    data = pd.read_csv("modified_%s" % filepath, sep='\t', quoting=csv.QUOTE_NONE,  skip_blank_lines=True)
    # data = add_sentence(data)
    data = naive_change_value(data, 'DEPREL', 'iobj', 'obl')
    data = naive_change_value(data, 'DEPREL', 'acl:inf', 'acl')
    data = naive_change_value(data, 'DEPREL', 'det:quant', 'det')
    data = change_COL1xCOL2(data, 'UPOSTAG', 'DEPREL', 'PRON', 'amod', new_col2_value='det')
    data = change_COL1xCOL2(data, 'XPOSTAG', 'DEPREL', 'PRON', 'amod', new_col2_value='det')
    data = change_COL1xFEATS(data, 'DEPREL', 'Prefix=Yes', new_col1_value="compound:affix")
    data = change_COL1xFEATS(data, 'DEPREL', 'VerbType=Cop', old_col1_value='aux', new_col1_value='cop')
    data = change_COL1xFEATS(data, 'UPOSTAG', 'VerbType=Cop', old_col1_value='VERB', new_col1_value='AUX')
    data = change_COL1xFEATS(data, 'XPOSTAG', 'VerbType=Cop', old_col1_value='VERB', new_col1_value='AUX')
    data = naive_change_value(data, 'DEPREL', 'conj:discourse', 'parataxis')
    data = change_COL1xCOL2(data, 'UPOSTAG', 'DEPREL', 'ADV', 'obl:tmod', new_col2_value='advmod')
    data = change_COL1xCOL2(data, 'XPOSTAG', 'DEPREL', 'ADV', 'obl:tmod', new_col2_value='advmod')
    data = naive_change_value(data, 'DEPREL', 'advmod:inf', 'acl')
    data = naive_change_value(data, 'DEPREL', 'aux:q', 'mark:q')
    data = naive_change_value(data, 'UPOSTAG', 'PART', 'ADP')
    data = naive_change_value(data, 'XPOSTAG', 'PART', 'ADP')
    data = change_COL1xCOL2(data, 'UPOSTAG', 'DEPREL', 'INTJ', 'advmod', new_col2_value='discourse')
    data = change_COL1xCOL2(data, 'XPOSTAG', 'DEPREL', 'INTJ', 'advmod', new_col2_value='discourse')
    data = predicative_complements_to_xcomp(data)
    data = change_dependent(data, 'UPOSTAG', 'ADV', 'DEPREL', 'dep', 'advmod', 'advmod:phrase')
    data = flip_aux_xcomp_for_modals(data)
    data = advmod_phrase_to_fixed(data)
    data = naive_change_value(data, 'DEPREL', 'advmod:phrase', 'advmod')
    # data.drop(columns=['SENTENCE'])
    data.to_csv('modified_%s' % filepath, sep='\t', index=False, header=False, quoting=csv.QUOTE_NONE)
    add_empty_lines(filepath)

def add_empty_lines(filepath):
    newfile = open('fixed_%s' % filepath, 'w')
    with open('modified_%s' % filepath, 'r') as f:
        f = f.readlines()
        for line in f:
            if 'sent_id' in line:
                newfile.write('\n')
                newfile.write(line)
            elif line.strip() == '':
                pass
            else:
                newfile.write(line)




if __name__ == "__main__":
    make_changes(training_treebank)




