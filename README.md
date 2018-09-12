# Hebrew UD
A library for handling treebanks, with focus on the Hebrew UD treebank HTB.
## Content:

### The HTB treebank
divided into 3 sections:
* dev - he_htb-ud-dev.conllu
* training - he_htb-ud-train.conllu
* test - he_htb-ud-test.conllu


### changes_to_treebank.py
A tool for investigation and conversion of the treebank. e.g. allows retrieval of all tokens that correspond to some attribute.

### lattices_builder.py
takes a raw sentence and builds a "lattices" file - one which all possible parses of each token are listed.
For example, the sentence שלום, היום יום יפה would yield the following lattice (in a conll-ul format):
```
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
```