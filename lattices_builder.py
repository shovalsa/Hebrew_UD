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
import pickle

prefixes = open('/home/shoval/repos/openU/data/bgulex/bgupreflex_withdef.utf8.hr', 'r').readlines()

prefixes = [line.split(" ") for line in prefixes]

prefix = [line[0] for line in prefixes]
# print(prefix)

def hash_lexicon(lexicon_path):
    lexicon = open(lexicon_path, 'r').readlines()
    lexicon = [line.split(" ") for line in lexicon]
    lex_dict = {}
    for word in lexicon:
        key = word[0]
        x = 0
        enum = 1
        d = {}
        while x < len(word) - 2:
            d[enum] = {'features': word[x+1][1:-1], 'lemma': word[x+2].strip()}
            x = x+2
            enum += 1
        lex_dict[key] = d
    with open('bgulex.pickle', 'wb') as handle:
        pickle.dump(lex_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)


def get_lexicon(pickle_path):
    with open(pickle_path, 'rb') as handle:
        return pickle.load(handle)

def print_morphs(lexicon):
    sentence = "שלום היום יום יפה והים מדהים"
    tokens = sentence.split(" ")
    print(tokens)
    for token in tokens:
        enum = len(token)
        while token[0:enum] not in prefix:
            enum -= 1
            if enum < 1:
                break
        pref = token[0:enum]
        if token in lexicon:
            print(lexicon[token])
        while token[len(pref):len(token)] not in lexicon:
            pref = pref[0:-1]
        if pref != "":
            if token[len(pref):len(token)] in lexicon:
                print(lexicon[token[len(pref):len(token)]])
                print("prefix", pref)




# hash_lexicon('/home/shoval/repos/openU/data/bgulex/bgulex.utf8.hr')
bgulex = get_lexicon('bgulex.pickle')
# print(bgulex['נחל'])
# print(bgulex['אשתגע'])
print_morphs(bgulex)
# נחל :NN-M-S: נחל :NNT-M-S: נחל :VB-M-S-3-PAST-PAAL: נחל :VB-M-S-2-IMPERATIVE-PAAL: נחל :VB-MF-P-1-FUTURE-HIFIL: החל
