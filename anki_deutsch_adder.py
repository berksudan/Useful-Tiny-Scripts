from collections import OrderedDict
from typing import List
import string
import re
import colorama
from colorama import Fore, Back, Style
import time
import os

def enter_category_index(category_keys:List[int]) -> int:
  category_indexes=[str(item) for item in list(range(len(category_keys)))]
  print('> Choose a category:')
  for i,category in zip(category_indexes,category_keys):
    print(f'    "{i}" for category: "{category}"')
  
  category_index = input("> Enter a category code:")

  while category_index not in category_indexes:
    category_index = input("> Given category code is not valid! Enter a category code:")

  return int(category_index)

def resolve_token(token:str) -> str:
  if token == '':
    pass
  elif token == "ICH_DU_ES":
    ich = input('   > Enter a conjugation for "ich" (add ` mich` at the end if reflexive):').lower()
    du = input('   > Enter a conjugation for "du" (add ` dich` at the end if reflexive):').lower()
    er_sie_es = input('   > Enter a conjugation for "er/sie/es" (add ` sich` at the end if reflexive):').lower()
    check_words = [ich.replace(' mich',''),du.replace(' dich',''),er_sie_es.replace(' sich','')]
    for word in check_words:
      if word.count(' ') > 1: return None
      if not word.replace(' ','').isalpha(): return None
    output = f'ich {ich}\ndu {du}\ner/sie/es {er_sie_es}'
  elif token == "WIR_IHR_SIE":
    wir = input('   > Enter a conjugation for "wir" (add ` uns` at the end if reflexive):').lower()
    ihr = input('   > Enter a conjugation for "ihr" (add ` euch` at the end if reflexive):').lower()
    Sie_sie = input('   > Enter a conjugation for "Sie/sie" (add ` sich` at the end if reflexive):').lower()
    check_words = [wir.replace(' uns',''),ihr.replace(' euch',''),Sie_sie.replace(' sich','')]
    for word in check_words:
      if word.count(' ') > 1: return None
      if not word.replace(' ','').isalpha(): return None
    output = f'wir {wir}\nihr {ihr}\nSie/sie {Sie_sie}'
  elif token == "ADJEKTIV":
    output = input("   > Enter an adjective:").lower()
    if not output.isalpha(): return None
  elif token == "ADJEKTIV_KOMPARATIV":
    output = input("   > Enter a comparative adjective:").lower()
    if not output.isalpha(): return None
  elif token == "ADJEKTIV_SUPERLATIV":
    output = input('   > Enter a superlativ adjective (without "am"):').lower()
    if not output.isalpha(): return None
  elif token.startswith("STR_GERMAN"):
    output = input("   > Enter a German text:")
  elif token.startswith("STR_ENGLISH"):
    output = input("   > Enter an English text:")
  elif token == "NOUN_SINGULAR":
    output = input("   > Enter a singular noun:").title()
    if not output.isalpha(): return None
  elif token == "VERB":
    output = input("   > Enter a verb (use `*` for trennbare Wörter, add ` sich` at the end if reflexive):").lower()
    if not output.replace('*','').replace(' sich','').isalpha(): return None
  elif token == "VERB_PERFEKT":
    output = input("   > Enter a verb in a perfekt form (add ` sich` at the end if reflexive):").lower()
    if not output.replace(' sich','').isalpha(): return None
  elif token == "ARTIKEL":
    output = input("   > Enter an artikel (der,die,das):").lower()
    if not output in ('der','die','das'):
      return None
  elif token == "HABEN_SEIN":
    output = input('   > Enter "haben", "sein" or "both":').lower()
    if not output in ('haben','sein','both'):
      return None
    if output == 'both':
      output = 'haben/sein'
  elif token == 'OPTIONAL_PLURAL':
    selection = input("   > Does this word have a plural form? (Y/n):").lower()
    if selection == 'n':
      output = 'NO PLURAL'
    else:  
      output = input("   > Enter a plural noun without artikel:").title()
      if not output.isalpha(): return None
      output = 'die ' + output
  else:
    raise Exception("Wrong Token")
  output = output.strip()
  if output == '': return None
  return output.strip()

def anki_deutsch_csv_row() -> str:
  categories = OrderedDict([
    ('ARTIKEL & PLURAL', '{NOUN_SINGULAR};{ARTIKEL} {NOUN_SINGULAR}, {OPTIONAL_PLURAL}'),
    ('AKKUSATIVFORM', '{STR_GERMAN1};{STR_GERMAN2}'),
    ('AUFFORDERUNG', '{STR_GERMAN};{STR_ENGLISH}'),
    ('DATIVFORM', '{STR_GERMAN1};{STR_GERMAN2}'),
    ('HABEN/SEIN + PERFEKT', '{VERB};{HABEN_SEIN} + {VERB_PERFEKT}'),
    ('IN ENG & ARTIKEL & PLURAL', '{NOUN_SINGULAR};{STR_ENGLISH}, {ARTIKEL} {NOUN_SINGULAR}, {OPTIONAL_PLURAL}'),
    ('IN ENG', '{STR_GERMAN};{STR_ENGLISH}'),
    ('KOMPARATIV & SUPERLATIV', '{ADJEKTIV};{ADJEKTIV_KOMPARATIV}, am {ADJEKTIV_SUPERLATIV}'),
    ('KOMPARATIV', '{ADJEKTIV};{ADJEKTIV_KOMPARATIV}'),
    ('KONJUGATION (ICH/DU/ES)', '{VERB};{ICH_DU_ES}'),
    ('KONJUGATION (WIR/IHR/SIE)', '{VERB};{WIR_IHR_SIE}'),
    ('QUIZFRAGE', '{STR_ENGLISH1};{STR_ENGLISH2}'),
    ('SUPERLATIV', '{ADJEKTIV};{ADJEKTIV_SUPERLATIV}'),
  ])

  category_index = enter_category_index(category_keys=categories.keys())

  selected_category = list(categories.items())[category_index]
  print(f'> Selected category: "{selected_category[0]}".')

  tokens = list(dict.fromkeys(re.findall('{(.*?)}', selected_category[1]))) 

  argument_pairs = {}
  for i,token in enumerate(tokens):
    print(f'> Token #{i} <{Fore.RED}{token}{Style.RESET_ALL}> in the pattern <{Back.YELLOW}{Fore.BLACK}{selected_category[1]}{Style.RESET_ALL}>:')
    output = resolve_token(token)
    while output is None:
      print('[ERROR] Output is None, please try again..')
      output = resolve_token(token)
    argument_pairs[token] = output

  output = f'{selected_category[0]}: {selected_category[1].format(**argument_pairs)}'
  print(f'> OUTPUT: "{Back.CYAN}{Fore.BLACK}{output}{Style.RESET_ALL}"')
  return output

def anki_deutsch_adder(filename:str):
  if os.path.exists(filename):
    with open(filename, "r") as fp:
      print(f'> INITIAL FILE CONTENT:{Fore.MAGENTA}',end='')
      lines =fp.readlines()
      if lines == []:
        print('<EMPTY>',end='')
        print(Style.RESET_ALL)
      else:
        for line in lines:
          print('\n  > ' + line[:-1],end='')
        print(Style.RESET_ALL)
        selection = input('> Do you want to erase the file content? (y/N)?:')
        if selection.lower() == 'y':
          with open(filename, "a+") as fp:
            fp.truncate(0)
            print('> File content deleted!')
            time.sleep(1.5)

  while True:
    with open(filename, "a+") as fp:
      try:
        output = anki_deutsch_csv_row()
        fp.write(output + '\n')
      except:
        print('\n> Exiting..')
        break

    with open(filename, "r") as fp:
      print(f'> CURRENT FILE CONTENT:{Fore.YELLOW}',end='')
      for line in fp.readlines():
        print('\n  > ' + line[:-1],end='')
      print(Style.RESET_ALL)

if __name__ == "__main__":
  anki_deutsch_adder(filename='new_anki_cards.csv')
  
