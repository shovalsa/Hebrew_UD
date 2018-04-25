from collections import Counter
import csv


def frequencies(filename, element, delim):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delim, quotechar='"', skipinitialspace=True)
        element_list = [row[element] for row in reader]
        return Counter(element_list)


def file_len(fname):
    enum = 0
    with open(fname) as f:
        for i, l in enumerate(f):
            if ('#' not in l) and ('PUNCT' not in l) and ('-' not in l):
                enum += 1
            pass
    return (i + 1, enum)

def noOfSentences(fname):
    enum = 0
    with open(fname) as f:
        for i, l in enumerate(f):
            if ("# sent_id" in l):
                enum += 1
            pass
    return (i + 1, enum)

print(file_len("/home/shoval/repos/openU/HTB/UD_Hebrew-HTB/he_htb-ud-test.conllu"))
print(noOfSentences("/home/shoval/repos/openU/HTB/UD_Hebrew-HTB/he_htb-ud-test.conllu"))

# freq = frequencies('data/he_treebank_dev.csv', 'UPOSTAG', ',')
# print(freq)
