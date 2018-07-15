from collections import Counter
import csv


def concat_files(files_list, new_file_name):
    with open(new_file_name, 'w') as outfile:
        for fname in files_list:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)

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

# print(file_len("/home/shoval/repos/openU/HTB/UD_Hebrew-HTB/he_htb-ud-dev.conllu"))
# print(noOfSentences("/home/shoval/repos/openU/HTB/UD_Hebrew-HTB/he_htb-ud-dev.conllu"))

freq = frequencies('entire_treebank_revised', 'DEPREL', '\t')
print(freq)

# filenames = ['fixed_he_htb-ud-dev.conllu', 'fixed_he_htb-ud-train.conllu', 'fixed_he_htb-ud-test.conllu']
# entire_treebank = concat_files(filenames, '/home/shoval/repos/openU/treebank-utilities/entire_treebank_revised')

