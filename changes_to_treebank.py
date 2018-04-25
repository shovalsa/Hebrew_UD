import re
import csv
import pandas as pd
import numpy as np

filepath = 'dummy_treebank.csv'
data = pd.read_csv(filepath, sep='\t', comment='#')


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
            data.at[data['FEATS'].str.contains(feature_value), col1] = new_col1_value
        else:
            data.at[(data['FEATS'].str.contains(feature_value)) & (data[col1] == old_col1_value), col1] = new_col1_value
    elif new_feature_value is not None:
        pass
        # need to find a way to edit a part of a string.
    return data


def make_changes(data):
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
    data.to_csv('output_pandas.csv', sep='\t')

# make_changes(data)


cop = data[data['UPOSTAG'] == 'NOUN']
shoval = data[data['UPOSTAG'] == 'NAME']
cop_head = cop['HEAD'] #Series([], Name: HEAD, dtype: object)
# print(cop_head)
# print(cop)
# cop.to_csv('cop.csv', sep='\t')
# print(data.describe())
sth = data.iloc[7]
# print(sth.name)
# print(type(sth)) #<class 'pandas.core.series.Series'>
# print(type(cop)) # <class 'pandas.core.frame.DataFrame'>
print(shoval)
print(type(shoval))

def get_head(dependent):
    head = dependent
    target_index = int(dependent['HEAD'])
    if target_index < int(dependent['INDEX']):
        while int(head['INDEX']) > target_index:
            try:
                head = data.iloc[int(head.name) - 1]
            except ValueError:
                head = data.iloc[int(head.name) - 2]
    elif target_index > int(dependent['INDEX']):
        while int(head['INDEX']) < target_index:
            try:
                head = data.iloc[int(head.name) + 1]
            except ValueError:
                head = data.iloc[int(head.name) + 2]
    return head


# print(sth)
for i, v in cop.iterrows():
    # print("i:", v)
    # print("v: ", v)
    print("dependent", v['HEAD'])
    print("head", get_head(v)['INDEX'])
