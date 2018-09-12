# encoding utf-8

"""
receives a sentence and a dictionary and creates a CoNLL-UL file which contains all possible morphological segmentations.
  the CoNLL-UL format should be:
FROM   TO     FORM   LEMMA  UPOS  CPOS  FEATURES                    MISC    ANCHORS
0-5 בצלם
0      5      BCLM   BCLM   PROPN   -
0      1      B      B      ADP     -                                       goldid=1
0      3      BCL    BCL    NOUN    -   Gender=Masc|Number=Sing
1      2      H      H      DET     -   PronType=Art                        goldid=2
1      3      CL     CL     NOUN    -   Gender=Masc|Number=Sing
2      3      CL     CL     NOUN    -   Gender=Masc|Number=Sing             goldid=3
2      5      CLM    CILM   VERB    -   Gender=Masc|Number=Si...
2      5      CLM    CILM   VERB    -   Gender=Masc|Mood=Imp...
2      5      CLM    CLM    NOUN    -   Definite=Cons|Gender=Mas...
2      5      CLM    CLM    NOUN    -   Gender=Masc|Number=Sing
3      4      FL     FL     ADP     -                                       goldid=4
4      5      HM     ANI    PRON    -   Gender=Masc|Number=Plur|Person=3    goldid=5
5-7    הנעים
5      7      HNEIM  HNEIM  VERB    -   Gender=Masc...
5      6      H      H      DET     -   PronType=Art                        goldid=6
5      6      H      H      SCONJ   -
6      7      NEIM   NEIM   ADJ     -   Gender=Masc|Number=Sing             goldid=7
6      7      NEIM   NEIM   ADJ     -   Definite=Cons|Gender=...
6      7      NEIM   NEIM   ADV     -   Polarity=Neg
6      7      NEIM   NEIM   AUX     -   Gender=Masc|Number=Sing...
6      7      NEIM   NEIM   PROPN   -
6      7      NEIM   NEIM   VERB    -   Gender=Masc|Tense=Part|VerbForm=Part
6      7      NEIM   NEIM   VERB    -   Gender=Masc|VerbForm=Part

"""
import time
import csv
import json

class LatticesBUilder(object):

    def __init__(self):
        self.csv_lexicon = self.get_lexicon_csv_as_list('../data/bgulex/heblex.csv')
        self.prefixes = self.get_prefixes_dict('../data/bgulex/bgupreflex_withdef.utf8.hr')
        self.conversion_table = self.get_conversion_table('../data/bgulex/conversion_spmrl_to_ud.csv')
        self.dict_lex = self.convert_lexicon_to_dict(self.csv_lexicon)



    def get_prefixes_dict(self, filepath):
        prefixes = open(filepath, 'r').readlines()
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
            # with open('../data/bgulex/morphemes.json', 'w') as jsonfile:
            #     json.dump(prefixes_dict, jsonfile, indent=4)
        return prefixes_dict


    def get_conversion_table(self, filepath):
        csvfile = open(filepath, 'r')
        conversion_table = csv.DictReader(csvfile, delimiter=',', quotechar='"', skipinitialspace=True)
        conversion_table = [dict for dict in conversion_table]

        return conversion_table

    def convert_atts(self, list_of_atts):
        spmrl, pos, features, suffix = [], [], [], []
        for att in list_of_atts:
            for dic in self.conversion_table:
                if dic['spmrl'] == att:
                    spmrl.append(dic['spmrl'])
                    pos.append(dic['pos'])
                    features.append(dic['features'])
                    suffix.append(dic['suffix'])
        features = "|".join(features)
        return spmrl, pos, features, suffix


    def replace_subtypes(self, word):
        if "DEF" in word:
            if ("\"" in word) or ("TTL" in word):
                word = word[4:] + "DEF"
            else:
                word = word[4:] + "X"
        if word[0] == ":":
            word = word[1:]
        if word[-1] == ":":
            word = word[:-1]
        return word


    def make_lexicon_dict(self, lexicon_path) -> dict:
        """
        :param lexicon_path: converts the lexicon from the bgulex format into a dictionary
        :return: a dict with the following structure: { "אאיר":
                        {1: {'LEMMA': 'האיר', 'FEATS': 'Gender=Fem,Masc|Number=Sing|Person=1|Tense=Fut|HebBinyan=HIFIL', 'SUFFIX': '', 'PREFIX': '', 'UPOSTAG': 'VERB'},
                        2: {'LEMMA': 'אייר', 'FEATS': 'Gender=Fem,Masc|Number=Sing|Person=1|Tense=Fut|HebBinyan=PIEL', 'SUFFIX': '', 'PREFIX': '', 'UPOSTAG': 'VERB'}}
                        }
        """
        lexicon = open(self, lexicon_path, 'r').readlines()
        lexicon = [line.split(" ") for line in lexicon]
        lex_dict = {}
        for word in lexicon:
            key = word[0]
            x = 0
            enum = 1
            d = {}
            while x < len(word) - 2:
                word[x+1] = self.replace_subtypes(word[x+1])
                semicolon = word[x+1].find(":")
                if ":" in word[x+1]:
                    atts = word[x + 1][:semicolon].split('-')
                    atts.append(word[x + 1][semicolon+1:])
                else:
                    atts = word[x + 1].split('-')
                spmrl, pos, features, suffix = convert_atts(atts)
                d[enum] = {'SPMRL': spmrl[-1], 'UPOSTAG': pos[0], 'FEATS': features[1:], 'SUFFIX': suffix[-1], 'LEMMA': word[x+2].strip()}
                x = x+2
                enum += 1
            lex_dict[key] = d
        return lex_dict


    def make_lex_list(self, lexicon_path) -> list:
        lexicon = open(lexicon_path, 'r').readlines()
        lexicon = [line.split(" ") for line in lexicon]
        lex_list = []
        for word in lexicon:
            d = {}
            d['form'] = word[0]
            x = 0
            enum = 1
            while x < len(word) - 2:
                word[x+1] = self.replace_subtypes(word[x+1])
                semicolon = word[x+1].find(":")
                if ":" in word[x+1]:
                    atts = word[x + 1][:semicolon].split('-')
                    atts.append(word[x + 1][semicolon+1:])
                else:
                    # atts = convert_atts(word[x + 1].split('-'))
                    atts = word[x + 1].split('-')
                spmrl, pos, features, suffix = self.convert_atts(atts)
                if 'X' not in features:
                    d[enum] = [spmrl[-1], pos[0], features[1:], suffix[-1], word[x+2].strip()]
                x = x+2
                enum += 1
            lex_list.append(d)

        return lex_list


    def make_csv(self, lex_filepath):
        conv_lex = self.make_lex_list(lex_filepath)
        with open('../data/bgulex/heblex.csv', 'w') as csvfile:
            fieldnames = ['form', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")

            # writer.writeheader()
            for row in conv_lex:
                try:
                    writer.writerow(row)
                except ValueError:
                    raise Exception(row)


    def make_json(self, lex_filepath):
        converted_lex = self.make_lexicon_dict(lex_filepath)
        with open('../data/bgulex/heblex.json', 'w', encoding="utf-8") as j:
            json.dump(converted_lex, j, indent=4)


    def get_lexicon_csv_as_dictreader(self, filepath):
        with open(filepath, 'r') as csvfile:
            fieldnames = ['form', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
            lexicon = csv.DictReader(csvfile, fieldnames, delimiter=';', quotechar='"', skipinitialspace=True)
            return [row for row in lexicon]


    def get_lexicon_csv_as_list(self, filepath):
        csvfile = open(filepath, 'r', encoding="utf-8")
        return csv.reader(csvfile, delimiter=';')


    def convert_lexicon_to_dict(self, lexicon):
        main_dict = {}
        for row in lexicon:
            main_dict[row[0]] = row[1]
        return main_dict



    def get_lexicon_json(self, filepath):
        with open(filepath, 'r') as jsonfile:
            return json.load(jsonfile)

    def segment_sentence(self, sentence) -> list:
        tokens = sentence.split(" ")
        after_segmentation = []
        for token in tokens:
            x = len(token)
            while x > 0:
                if token[0:x] in self.prefixes:
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

    def get_items_from_lex(self, segmented_text, lexicon, prefixes):
        syntax = []
        for tup in segmented_text:
            if tup[0] == 'lexical_word':
                for row in lexicon:
                    if row[0] == tup[1]:
                        syntax.append(row)
                        break

    def tmp(self, segmented):
        for s in segmented:
            if s[0] == 'morpheme':
                for v in self.prefixes[s[1]].values():
                    for morph, tag in v.items():
                        print(morph, '\t', tag)
            elif s[1] in self.dict_lex:
                for version in self.dict_lex[s[1]].values():
                    if version['PREFIX'] != '':
                        print(version['PREFIX'])
                    print(version['UPOSTAG'], '\t', version['FEATS'], '\t', version['LEMMA'])
                    if version['SUFFIX'] != '':
                        print(version['SUFFIX'])
            else:
                print(s[1], 'UNK')


    segmented = segment_sentence(sentence="יש משקאות משכרים על המדף")
    # [('lexical_word', 'יש'), ('lexical_word', 'משקאות'), ('morpheme', 'מש'), ('lexical_word', 'קאות'), ('morpheme', 'מ'),
    #  ('lexical_word', 'שקאות'), ('lexical_word', 'משכרים'), ('morpheme', 'משכ'), ('lexical_word', 'רים'),
    # ('morpheme', 'מש'), ('lexical_word', 'כרים'), ('morpheme', 'מ'), ('lexical_word', 'שכרים'), ('lexical_word', 'על'),
    # ('lexical_word', 'המדף'), ('morpheme', 'ה'), ('lexical_word', 'מדף')]
    print(segmented)
