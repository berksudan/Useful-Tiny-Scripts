import csv
import pprint
from collections import defaultdict
import os
import re

HTML_TAGS_TO_REAL_SYMBOLS = {
    '&#x27;': '\'',
    '&quot;': '"',
    '&amp;': '&',
    '&nbsp;': ' ',
    '&gt;': '>',
}
DATA_FILENAME = 'input_deck/Deutsche Übung.txt'
DATA_DELIMITER = '\t'
OUTPUT_DELIMITER = ';'
TAG_DEU_TO_ENG = 'DEU -> ENG'
TAG_ENG_TO_DEU = 'ENG -> DEU'
CATEGORY_DEU_TO_ENG = f'{TAG_DEU_TO_ENG}:'
CATEGORY_ENG_TO_DEU = f'{TAG_ENG_TO_DEU}:'
CATEGORY_DEU_TO_ENG_ARTIKEL_PLURAL = 'DEU -> ENG & ARTIKEL & PLURAL:'

# Generate output filename based on input filename
output_base_name = os.path.splitext(DATA_FILENAME.split('/')[-1])[0]
OUTPUT_NEW_ENTRIES_FILENAME = f'output/{output_base_name}__new_translations.csv'
OUTPUT_UPDATED_ENTRIES_FILENAME = f'output/{output_base_name}__updated_translations.csv'

pp = pprint.PrettyPrinter(indent=4)

def check_data_integrity(filename, delimiter):

    pattern = re.compile(r'&\w+;')
    offending_lines = []

    with open(filename, 'r') as fp:
        tsvreader = csv.reader(fp, delimiter=delimiter)
        for row in tsvreader:
            if row[0].startswith('#separator:') or row[0].startswith('#html:') or row[0].startswith('#tags column:'):
                continue
            if len(row) < 2 or not row[0].strip() or not row[1].strip():
                offending_lines.append(row)
                continue
            for field in row[:2]:
                if pattern.search(field):
                    offending_lines.append(row)
                    break

    if len(offending_lines) > 0:
        for line in offending_lines:
            print(f'> Offending line: {line}')

        print(f'> Use this table to replace these characters in the Anki deck:')
        for key, val in HTML_TAGS_TO_REAL_SYMBOLS.items():
            print(f'\t{key} -> <{val}>')

        raise ValueError('Dataset contains invalid HTML entities, empty strings in the first two columns, or similar patterns.')

def read_deu_to_eng_data(filename, delimiter, tag_deu_to_eng):
    with open(filename, 'r') as fp:
        tsvreader = csv.reader(fp, delimiter=delimiter)
        return [row[:2] for row in tsvreader if tag_deu_to_eng in row[0]]

def read_eng_to_deu_data(filename, delimiter, tag_eng_to_deu):
    with open(filename, 'r') as fp:
        tsvreader = csv.reader(fp, delimiter=delimiter)
        return [row[:2] for row in tsvreader if tag_eng_to_deu in row[0]]

def extract_deu_to_eng_word_tuples(data, category_deu_to_eng, category_deu_to_eng_artikel_plural):
    en_de_word_tuples = []
    for row in data:
        category, value = row[0], row[1].strip()
        if category.startswith(category_deu_to_eng):
            de_word = category[len(category_deu_to_eng):].strip()
            en_word = value
        elif category.startswith(category_deu_to_eng_artikel_plural):
            de_word = value.split(',')[1].strip()
            en_word = value.split(',')[0].strip()
        else:
            raise ValueError(f'Unexpected category in row: {row[0]}')
        en_de_word_tuples.append((en_word, de_word))
    return en_de_word_tuples

def extract_eng_to_deu_word_tuples(data, category_eng_to_deu):
    de_en_word_tuples = []
    for row in data:
        category, value = row[0], row[1].strip()
        if category.startswith(category_eng_to_deu):
            en_word = category[len(category_eng_to_deu):].strip()
            de_word = value
        else:
            raise ValueError(f'Unexpected category in row: {row[0]}')
        de_en_word_tuples.append((en_word, de_word))
    return de_en_word_tuples

def build_translation_dict(en_de_word_tuples):
    en_to_de_dict = defaultdict(set)
    for en_word, de_word in en_de_word_tuples:
        en_words = en_word.split(' | ')
        for word in en_words:
            en_to_de_dict[word.strip()].add(de_word)
    return {en: ' | '.join(sorted(de_list)) for en, de_list in en_to_de_dict.items()}

def filter_existing_translations(dict_eng_to_deu_candidates, data_eng_to_deu_existent):
    
    new_entries = {}
    updated_entries = {}
    
    for key, value in dict_eng_to_deu_candidates.items():
        if key in dict_eng_to_deu_existent:
            if dict_eng_to_deu_existent[key] != value:
                new_vals = value.split(' | ')
                existent_vals = dict_eng_to_deu_existent[key].split(' | ')
                if set(new_vals) - set(existent_vals):
                    updated_entries[key] = ' | '.join(sorted(set(new_vals) | set(existent_vals)))
        else:
            new_entries[key] = value
    
    return new_entries, updated_entries

def build_new_translation_lines(entries:dict,category:str,filename:str):
    entry_lines = []
    for key, value in entries.items():
        entry_lines.append(f'{category} {key}{OUTPUT_DELIMITER}{value}')

    with open(filename, 'w') as f:
        for line in entry_lines:
            f.write(line + '\n')


# Check for HTML entities and empty strings in the first two columns before processing
check_data_integrity(DATA_FILENAME, DATA_DELIMITER)

data_deu_to_eng = read_deu_to_eng_data(DATA_FILENAME, DATA_DELIMITER, TAG_DEU_TO_ENG)
en_de_word_tuples = extract_deu_to_eng_word_tuples(data_deu_to_eng, CATEGORY_DEU_TO_ENG, CATEGORY_DEU_TO_ENG_ARTIKEL_PLURAL)
dict_eng_to_deu_candidates = build_translation_dict(en_de_word_tuples)

data_eng_to_deu = read_eng_to_deu_data(DATA_FILENAME, DATA_DELIMITER, TAG_ENG_TO_DEU)
de_en_word_tuples = extract_eng_to_deu_word_tuples(data_eng_to_deu, CATEGORY_ENG_TO_DEU)
dict_eng_to_deu_existent = build_translation_dict(de_en_word_tuples)

new_entries, updated_entries = filter_existing_translations(dict_eng_to_deu_candidates, dict_eng_to_deu_existent)

print("\nNew entries to be added:")
pp.pprint(new_entries)
print("\nEntries to be updated:")
pp.pprint(updated_entries)

build_new_translation_lines(new_entries, CATEGORY_ENG_TO_DEU,OUTPUT_NEW_ENTRIES_FILENAME)
build_new_translation_lines(updated_entries,CATEGORY_ENG_TO_DEU,OUTPUT_UPDATED_ENTRIES_FILENAME)
