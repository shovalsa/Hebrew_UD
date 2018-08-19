# encoding utf-8

"""
receives a sentence and a dictionary and creates a CoNLL-UL file which contains all possible morphological segmentations.
  the CoNLL-UL format should be:
FROM    TO   FORM    LEMMA   UPOS  CPOS   FEATURES    MISC    ANCHORS
0	1	ש	ש	REL	REL	_	1
0	2	שלום	שליו	NN	NN	gen=M|num=S|suf_gen=M|suf_num=P|suf_per=3	1
0	2	שלום	שלום	NN	NN	gen=M|num=S	1
0	2	שלום	שלום	INTJ	INTJ	_	1
0	2	שלום	שלום	NNT	NNT	gen=M|num=S	1
0	2	שלום	שלום	NNP	NNP	gen=M|num=S	1
1	2	לום	לום	NNT	NNT	gen=M|num=S	1
1	2	לום	לום	NN	NN	gen=M|num=S	1
2	3	,	_	yyCM	yyCM	_	2
3	4	ה	ה	DEF	DEF	_	3
3	5	ה	ה	REL	REL	_	3
3	6	היום	היום	RB	RB	_	3
4	6	יום	יום	NNT	NNT	gen=M|num=S	3
4	6	יום	יום	NN	NN	gen=M|num=S	3
5	6	יום	יום	NNT	NNT	gen=M|num=S	3
5	6	יום	יום	NN	NN	gen=M|num=S	3
6	7	יום	יום	NNT	NNT	gen=M|num=S	4
6	7	יום	יום	NN	NN	gen=M|num=S	4
7	8	יפה	יפה	JJ	JJ	gen=F|num=S	5
7	8	יפה	יפה	VB	VB	gen=M|num=S|per=3|tense=PAST	5
7	8	יפה	יפה	JJT	JJT	gen=M|num=S	5
7	8	יפה	יפה	JJ	JJ	gen=M|num=S	5
7	8	יפה	יפה	RB	RB	_	5
7	8	יפה	יפה	INTJ	INTJ	_	5
7	8	יפה	יפה	NNP	NNP	gen=F|num=S	5
7	8	יפה	ייפה	VB	VB	gen=M|num=S|per=3|tense=PAST	5
7	8	יפה	ייפה	VB	VB	gen=M|num=S|per=2|tense=IMPERATIVE	5
8	9	0	_	yyDOT	yyDOT	_	6


אאבן :VB-MF-S-1-FUTURE-PIEL: איבן

"""
import time
import csv
import json

def get_prefixes():
    prefixes = open('/home/shoval/repos/openU/data/bgulex/bgupreflex_withdef.utf8.hr', 'r').readlines()
    prefixes = [line.split(" ") for line in prefixes]
    prefixes_dict = {}
    for p in prefixes:
        morph_dict = {}
        # morph_dict['form'] = p[0]
        enum = 1
        while enum < len(p) - 1:
            morphemes = p[enum].split("^")
            pos = p[enum+1].strip().replace(":", "").split("+")
            enum += 2
            morph_dict[enum-2] = dict(zip(morphemes, pos))
        prefixes_dict[p[0]] = morph_dict
        # with open('/home/shoval/repos/openU/data/bgulex/morphemes.json', 'w') as jsonfile:
        #     json.dump(prefixes_dict, jsonfile, indent=4)
    return prefixes_dict


prefixes = get_prefixes()
# for p in prefixes:
#     print(p)

def get_conversion_table():
    csvfile = open('/home/shoval/repos/openU/data/bgulex/conversion_spmrl_to_ud.csv', 'r')
    conversion_table = csv.DictReader(csvfile, delimiter=',', quotechar='"', skipinitialspace=True)
    conversion_table = [dict for dict in conversion_table]

    return conversion_table

def convert_atts(list_of_atts):
    conversion_table = get_conversion_table()
    prefix, pos, features, suffix = [], [], [], []
    for att in list_of_atts:
        for dic in conversion_table:
            if dic['spmrl'] == att:
                prefix.append(dic['prefix'])
                pos.append(dic['pos'])
                features.append(dic['features'])
                suffix.append(dic['suffix'])
    features = "|".join(features)
    return prefix, pos, features, suffix


def replace_subtypes(word):
    if "DEF" in word:
        word = word[4:] + "DEF"
    if word[0] == ":":
        word = word[1:]
    if word[-1] == ":":
        word = word[:-1]
    return word


def make_lexicon_dict(lexicon_path) -> dict:
    """
    :param lexicon_path: converts the lexicon from the bgulex format into a dictionary
    :return: a dict with the following structure: { "אאיר":
                    {1: {'LEMMA': 'האיר', 'FEATS': 'Gender=Fem,Masc|Number=Sing|Person=1|Tense=Fut|HebBinyan=HIFIL', 'SUFFIX': '', 'PREFIX': '', 'UPOSTAG': 'VERB'},
                    2: {'LEMMA': 'אייר', 'FEATS': 'Gender=Fem,Masc|Number=Sing|Person=1|Tense=Fut|HebBinyan=PIEL', 'SUFFIX': '', 'PREFIX': '', 'UPOSTAG': 'VERB'}}
                    }
    """
    lexicon = open(lexicon_path, 'r').readlines()
    lexicon = [line.split(" ") for line in lexicon]
    lex_dict = {}
    for word in lexicon:
        key = word[0]
        x = 0
        enum = 1
        d = {}
        while x < len(word) - 2:
            word[x+1] = replace_subtypes(word[x+1])
            semicolon = word[x+1].find(":")
            if ":" in word[x+1]:
                atts = word[x + 1][:semicolon].split('-')
                atts.append(word[x + 1][semicolon+1:])
            else:
                atts = word[x + 1].split('-')
            prefix, pos, features, suffix = convert_atts(atts)
            d[enum] = {'PREFIX': prefix[-1], 'UPOSTAG': pos[0], 'FEATS': features[1:], 'SUFFIX': suffix[-1], 'LEMMA': word[x+2].strip()}
            x = x+2
            enum += 1
        lex_dict[key] = d
    return lex_dict


def make_lex_list(lexicon_path) -> list:
    lexicon = open(lexicon_path, 'r').readlines()
    lexicon = [line.split(" ") for line in lexicon]
    lex_list = []
    for word in lexicon:
        d = {}
        d['form'] = word[0]
        x = 0
        enum = 1
        while x < len(word) - 2:
            word[x+1] = replace_subtypes(word[x+1])
            semicolon = word[x+1].find(":")
            if ":" in word[x+1]:
                atts = word[x + 1][:semicolon].split('-')
                atts.append(word[x + 1][semicolon+1:])
            else:
                # atts = convert_atts(word[x + 1].split('-'))
                atts = word[x + 1].split('-')
            prefix, pos, features, suffix = convert_atts(atts)
            d[enum] = [prefix[-1], pos[0], features[1:], suffix[-1], word[x+2].strip()]
            x = x+2
            enum += 1
        lex_list.append(d)

    return lex_list


def make_csv(lex_filepath):
    conv_lex = make_lex_list(lex_filepath)
    with open('/home/shoval/repos/openU/data/bgulex/heblex.csv', 'w') as csvfile:
        fieldnames = ['form', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # writer.writeheader()
        for row in conv_lex:
            try:
                writer.writerow(row)
            except ValueError:
                raise Exception(row)


def make_json(lex_filepath):
    converted_lex = make_lexicon_dict(lex_filepath)
    with open('/home/shoval/repos/openU/data/bgulex/heblex.json', 'w', encoding="utf-8") as j:
        json.dump(converted_lex, j, indent=4)


def get_lexicon_csv(filepath):
    with open(filepath, 'r') as csvfile:
        fieldnames = ['form', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
        lexicon = csv.DictReader(csvfile, fieldnames, delimiter=',', quotechar='"', skipinitialspace=True)
        return [row for row in lexicon]

def get_lexicon_json(filepath):
    with open(filepath, 'r') as jsonfile:
        return json.load(jsonfile)

def segment_sentence(sentence) -> list:
    prefixes = get_prefixes()
    tokens = sentence.split(" ")
    after_segmentation = []
    for token in tokens:
        x = len(token)
        while x > 0:
            if token[0:x] in prefixes:
                after_segmentation.append(('morpheme', token[0:x]))
                after_segmentation.append(('lexical_word', token[x:]))
            else:
                if len(after_segmentation) != 0:
                    if ('lexical_word', token) != after_segmentation[-1]:
                        after_segmentation.append(('lexical_word', token))
                else:
                    after_segmentation.append(('lexical_word', token))
            x -= 1
    return after_segmentation




# csv_lexicon = get_lexicon_csv('/home/shoval/repos/openU/data/bgulex/heblex.csv')
start_time = time.time()
json_lexicon = get_lexicon_json('/home/shoval/repos/openU/data/bgulex/heblex.json')
prefixes = get_prefixes()
print(time.time() - start_time)
start_time = time.time()

segmented = segment_sentence(sentence="אני בבית")
for s in segmented:
    if s[0] == 'morpheme':
        for v in prefixes[s[1]].values():
            for morph, tag in v.items():
                print(morph, '\t', tag)
    elif s[1] in json_lexicon:
        for version in json_lexicon[s[1]].values():
            if version['PREFIX'] != '':
                print(version['PREFIX'])
            print(version['UPOSTAG'], '\t', version['FEATS'], '\t', version['LEMMA'])
            if version['SUFFIX'] != '':
                print(version['SUFFIX'])

        # print(s)
    else:
        print(s[1], 'UNK')

print(time.time() - start_time)
