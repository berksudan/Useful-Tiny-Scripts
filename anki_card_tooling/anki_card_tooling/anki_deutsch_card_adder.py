import readline
from collections import OrderedDict
from typing import List, Optional
import re
import os
import time

BACK_CYAN = "\x1b[46m"  # Taken from the Back.CYAN of the Colorama package
BACK_YELLOW = "\x1b[43m"  # Taken from the Back.YELLOW of the Colorama package
FORE_BLACK = "\x1b[30m"  # Taken from the Fore.BLACK of the Colorama package
FORE_MAGENTA = "\x1b[35m"  # Taken from the Fore.MAGENTA of the Colorama package
FORE_RED = "\x1b[31m"  # Taken from the Fore.RED of the Colorama package
FORE_YELLOW = "\x1b[33m"  # Taken from the Fore.YELLOW of the Colorama package
STYLE_RESET_ALL = "\x1b[0m"  # Taken from the Style.RESET_ALL of the Colorama package


def enter_category_index(category_keys: List[int]) -> int:
    category_indexes = [str(item) for item in list(range(len(category_keys)))]
    print("> Choose a category:")
    for i, category in zip(category_indexes, category_keys):
        print(f'    "{i}" for category: "{category}"')

    category_index = input("> Enter a category code:")

    while category_index not in category_indexes:
        category_index = input(
            "> Given category code is not valid! Enter a category code:"
        )

    return int(category_index)


def enter_from_options(options: List[str], output_upper_case: bool = True):
    quoted_opt = list(map(lambda x: f'"{x}"', options))
    output = input(
        f'   > Enter {", ".join(quoted_opt[:-1])} or {quoted_opt[-1]}:'
    ).lower()
    if not output in options:
        return None
    if output_upper_case:
        output = output.upper()
    return output



def resolve_token(token: str) -> str | None:
    """
    Prompt the user to resolve various token types into their string outputs.
    Returns the trimmed output or None if the input was invalid/empty.
    """
    match token:
        case "":  # empty token → no action
            return None

        case "ICH_DU_ES":
            ich = input(
                '   > Enter a conjugation for "ich" (add ` mich` at the end if reflexive): '
            ).lower()
            du = input(
                '   > Enter a conjugation for "du" (add ` dich` at the end if reflexive): '
            ).lower()
            er_sie_es = input(
                '   > Enter a conjugation for "er/sie/es" (add ` sich` at the end if reflexive): '
            ).lower()

            # Validate that each cleaned word is single‑ or two‑part and alphabetic
            for word in (ich.replace(" mich", ""), du.replace(" dich", ""), er_sie_es.replace(" sich", "")):
                if word.count(" ") > 1 or not word.replace(" ", "").isalpha():
                    return None

            output = f"ich {ich}<br>du {du}<br>er/sie/es {er_sie_es}"

        case "WIR_IHR_SIE":
            wir = input(
                '   > Enter a conjugation for "wir" (add ` uns` at the end if reflexive): '
            ).lower()
            ihr = input(
                '   > Enter a conjugation for "ihr" (add ` euch` at the end if reflexive): '
            ).lower()
            sie_sie = input(
                '   > Enter a conjugation for "Sie/sie" (add ` sich` at the end if reflexive): '
            ).lower()

            for word in (wir.replace(" uns", ""), ihr.replace(" euch", ""), sie_sie.replace(" sich", "")):
                if word.count(" ") > 1 or not word.replace(" ", "").isalpha():
                    return None

            output = f"wir {wir}<br>ihr {ihr}<br>Sie/sie {sie_sie}"

        case "ADJEKTIV":
            adj = input("   > Enter an adjective: ").lower()
            if not adj.isalpha():
                return None
            output = adj

        case "ADJEKTIV_KOMPARATIV":
            comp = input("   > Enter a comparative adjective: ").lower()
            if not comp.isalpha():
                return None
            output = comp

        case "ADJEKTIV_SUPERLATIV":
            superl = input('   > Enter a superlativ adjective (without "am"): ').lower()
            if not superl.isalpha():
                return None
            output = superl

        case t if t.startswith("STR_GERMAN"):
            output = input("   > Enter a German text: ")

        case t if t.startswith("STR_ENGLISH"):
            output = input("   > Enter an English text: ")

        case t if t.startswith("STR_ANY"):
            output = input("   > Enter any text: ")

        case "NOUN_SINGULAR":
            noun = input("   > Enter a singular noun: ").title()
            if not noun.isalpha():
                return None
            output = noun

        case t if t.startswith("VERB_"):
            form = t.split("VERB_")[1].lower()
            assert form in ("present", "perfekt", "präteritum")
            verb = input(
                f"   > Enter a verb in {form} form (add `sich ` at the beginning if reflexive): "
            ).lower()
            cleaned = verb.replace("*", "").replace("sich ", "").replace(" ", "")
            if not cleaned.isalpha():
                return None
            output = verb

        case "ARTIKEL":
            output = enter_from_options(["der", "die", "das"], output_upper_case=False)

        case "HAT_IST":
            choice = enter_from_options(["hat", "ist", "both"], output_upper_case=True)
            output = "HAT/IST" if choice == "BOTH" else choice

        case "AKK_DAT":
            output = enter_from_options(["akkusativ", "dativ"], output_upper_case=True)

        case "PREPOSITION":
            preps = [
                "an", "auf", "aus", "bei", "durch", "für", "gegen",
                "mit", "nach", "ohne", "um", "unter", "über", "von", "vor", "zu",
            ]
            output = enter_from_options(preps, output_upper_case=True)

        case "OPTIONAL_PLURAL":
            sel = input("   > Does this word have a plural form? (Y/n): ").lower()
            if sel == "n":
                output = "NO PLURAL"
            else:
                pl = input("   > Enter a plural noun without artikel: ").title()
                if not pl.isalpha():
                    return None
                output = f"die {pl}"

        case _:  # fallback for any other token
            raise ValueError("Wrong Token")

    # Final cleanup and empty‑string check
    result = output.strip()
    return result if result else None


def anki_deutsch_csv_row() -> str:
    categories = OrderedDict(
        [
            (
                "ARTIKEL ⋀ PLURAL",
                "{NOUN_SINGULAR};{ARTIKEL} {NOUN_SINGULAR}, {OPTIONAL_PLURAL}",
            ),
            ("AKKUSATIVFORM", "{STR_GERMAN_1};{STR_GERMAN_2}"),
            ("AUFFORDERUNG", "{STR_GERMAN};{STR_ENGLISH}"),
            ("DATIVFORM", "{STR_GERMAN_1};{STR_GERMAN_2}"),
            ("HAT/IST + PERFEKT", "{VERB_PRESENT};{HAT_IST} + {VERB_PERFEKT}"),
            (
                "PRÄTERITUM ⋀ HAT/IST + PERFEKT",
                "{VERB_PRESENT};{VERB_PRÄTERITUM}, {HAT_IST} + {VERB_PERFEKT}",
            ),
            (
                "DEU → ENG ⋀ ARTIKEL ⋀ PLURAL",
                "{NOUN_SINGULAR};{STR_ENGLISH}, {ARTIKEL} {NOUN_SINGULAR}, {OPTIONAL_PLURAL}",
            ),
            ("DEU → ENG", "{STR_GERMAN};{STR_ENGLISH}"),
            (
                "KOMPARATIV ⋀ SUPERLATIV",
                "{ADJEKTIV};{ADJEKTIV_KOMPARATIV}, am {ADJEKTIV_SUPERLATIV}",
            ),
            ("KOMPARATIV", "{ADJEKTIV};{ADJEKTIV_KOMPARATIV}"),
            ("KONJUGATION (ICH/DU/ES)", "{VERB_PRESENT};{ICH_DU_ES}"),
            ("KONJUGATION (WIR/IHR/SIE)", "{VERB_PRESENT};{WIR_IHR_SIE}"),
            (
                "PRÄPOSITION ⋀ AKKUSATIV/DATIV",
                "{VERB_PRESENT};{VERB_PRESENT} + {PREPOSITION} + {AKK_DAT}",
            ),
            ("QUIZFRAGE", "{STR_ANY_1};{STR_ANY_2}"),
            ("SUPERLATIV", "{ADJEKTIV};{ADJEKTIV_SUPERLATIV}"),
        ]
    )

    category_index = enter_category_index(category_keys=categories.keys())

    selected_category = list(categories.items())[category_index]
    print(f'> Selected category: "{selected_category[0]}".')

    tokens = list(dict.fromkeys(re.findall("{(.*?)}", selected_category[1])))

    argument_pairs = {}
    for i, token in enumerate(tokens):
        print(
            f"> Token #{i} <{FORE_RED}{token}{STYLE_RESET_ALL}> in the pattern <{BACK_YELLOW}{FORE_BLACK}{selected_category[1]}{STYLE_RESET_ALL}>:"
        )
        output = resolve_token(token)
        while output is None:
            print("[ERROR] Output is None, please try again..")
            output = resolve_token(token)
        argument_pairs[token] = output

    output = f"{selected_category[0]}: {selected_category[1].format(**argument_pairs)}"
    print(f'> OUTPUT: "{BACK_CYAN}{FORE_BLACK}{output}{STYLE_RESET_ALL}"')
    return output


def anki_deutsch_adder(filename: str):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as fp:
            print(f"> INITIAL FILE CONTENT:{FORE_MAGENTA}", end="")
            lines = fp.readlines()
            if lines == []:
                print("<EMPTY>", end="")
                print(STYLE_RESET_ALL)
            else:
                for line in lines:
                    print("\n  > " + line[:-1], end="")
                print(STYLE_RESET_ALL)
                selection = input("> Do you want to erase the file content? (y/N)?:")
                if selection.lower() == "y":
                    with open(filename, "a+", encoding="utf-8") as fp:
                        fp.truncate(0)
                        print("> File content deleted!")
                        time.sleep(1.5)

    while True:
        with open(filename, "a+", encoding="utf-8") as fp:
            try:
                output = anki_deutsch_csv_row()
                fp.write(output + "\n")
            except KeyboardInterrupt as e:
                print(f"\n> Got: {e}, exiting..")
                break

        with open(filename, "r", encoding="utf-8") as fp:
            print(f"> CURRENT FILE CONTENT:{FORE_YELLOW}", end="")
            for line in fp.readlines():
                print("\n  > " + line[:-1], end="")
            print(STYLE_RESET_ALL)


if __name__ == "__main__":
    anki_deutsch_adder(filename="output/new_anki_cards.csv")
