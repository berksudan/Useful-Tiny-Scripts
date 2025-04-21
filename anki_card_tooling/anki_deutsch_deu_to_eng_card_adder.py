#!/usr/bin/env python3

import re
import csv
import pprint
from pathlib import Path
from enum import Enum
from typing import (
    Final,
    List,
    Tuple,
    Dict,
    Set,
    Pattern,
)
from typing_extensions import Literal
from dataclasses import dataclass

#─── Constants ────────────────────────────────────────────────────────────────

#: Mapping of HTML entities to their literal replacements
HTML_CATEGORYS_TO_REAL_SYMBOLS: Final[Dict[str, str]] = {
    "&#x27;": "'",
    "&quot;": '"',
    "&amp;": "&",
    "&nbsp;": " ",
    "&gt;": ">",
}

NO_SINGULAR_TAG = "NO SINGULAR"


@dataclass(frozen=True,kw_only=True)
class InputData:
    """Input deck configuration."""
    FILEPATH: Final[Path] = Path("input_deck") / "Deutsche Übung.txt"
    FILENAME = FILEPATH.stem
    DELIMITER: Final[Literal["\t"]] = "\t"

@dataclass(frozen=True,kw_only=True)
class OutputData:
    """Output files and directories."""
    DELIMITER: Final[Literal[";"]] = ";"
    PARENT_DIR: Final[Path] = Path("output")
    NEW_ENTRIES_FILEPATH = f"{PARENT_DIR}/new_translations.csv"
    UPDATED_ENTRIES_FILEPATH = f"{PARENT_DIR}/updated_translations.csv"

@dataclass(frozen=True,kw_only=True)
class DeuToEng:
    """German→English tags in the deck."""
    CATEGORY = "DEU → ENG"
    PREFIX_SIMPLE = f"{CATEGORY}:"
    PREFIX_ARTIKEL_PLURAL = f"{CATEGORY} ⋀ ARTIKEL ⋀ PLURAL:"

@dataclass(frozen=True,kw_only=True)
class EngToDeu:
    """English→German tags in the deck."""
    CATEGORY = "ENG → DEU"
    PREFIX_SIMPLE = f"{CATEGORY}:"


pp: Final[pprint.PrettyPrinter] = pprint.PrettyPrinter(indent=4)

#─── Functions ────────────────────────────────────────────────────────────────

def check_data_integrity(
    filepath: Path,
    delimiter: str
) -> None:
    """
    Verify that the first two columns of the TSV do not contain empty values
    or HTML-entity patterns like &...; (except in the #separator/html/tags lines).
    Raises ValueError if any offending rows are found.
    """
    pattern: Pattern[str] = re.compile(r"&\w+;")
    offending: List[List[str]] = []

    with filepath.open("r", encoding="utf-8") as fp:
        reader = csv.reader(fp, delimiter=delimiter)
        for row in reader:
            if any(row[0].startswith(pref) for pref in ("#separator:", "#html:", "#tags column:")):
                continue
            if len(row) < 2 or not row[0].strip() or not row[1].strip():
                offending.append(row)
                continue
            if pattern.search(row[0]) or pattern.search(row[1]):
                offending.append(row)

    if offending:
        for row in offending:
            print(f"> Offending line: {row}")
        print("> Use this mapping to replace in Anki deck:")
        for src, tgt in HTML_CATEGORYS_TO_REAL_SYMBOLS.items():
            print(f"\t{src} -> {tgt}")
        raise ValueError("Dataset contains invalid HTML entities or empty first-two columns.")


def read_tuples(
    filepath: Path,
    delimiter: str,
    category: str
) -> List[Tuple[str, str]]:
    """
    Read all rows containing `category` in the first column, returning a list of
    (category, value) tuples (first two columns only, value stripped).
    """
    out: List[Tuple[str, str]] = []
    with filepath.open("r", encoding="utf-8") as fp:
        reader = csv.reader(fp, delimiter=delimiter)
        for row in reader:
            if category in row[0]:
                out.append((row[0], row[1].strip()))
    return out


def extract_deu_to_eng(
    data: List[Tuple[str, str]],
    prefix_simple: str,
    prefix_artikel_plural: str
) -> List[Tuple[str, str]]:
    """
    From raw DEU → ENG rows, extract (english, german) tuples.
    Handles normal entries and 'Artikel ⋀ Plural' entries.
    """
    out: List[Tuple[str, str]] = []
    for cat, val in data:
        if cat.startswith(prefix_simple):
            de_word = cat[len(prefix_simple):].strip()
            en_word = val
        elif cat.startswith(prefix_artikel_plural):
            parts = [p.strip() for p in val.split(",")]
            en_word = parts[0]
            de_word = parts[1] if parts[1] != NO_SINGULAR_TAG else parts[2]
        else:
            raise ValueError(f"Unexpected category in row: {cat!r}")
        out.append((en_word, de_word))
    return out


def extract_eng_to_deu(
    data: List[Tuple[str, str]],
    prefix_simple: str
) -> List[Tuple[str, str]]:
    """
    From raw ENG → DEU rows, extract (english, german) tuples.
    """
    out: List[Tuple[str, str]] = []
    for cat, val in data:
        if cat.startswith(prefix_simple):
            en_word = cat[len(prefix_simple):].strip()
            de_word = val
        else:
            raise ValueError(f"Unexpected category in row: {cat!r}")
        out.append((en_word, de_word))
    return out


def build_translation_dict(
    pairs: List[Tuple[str, str]]
) -> Dict[str, str]:
    """
    Build a dict mapping each English word (or phrase) to its German translations,
    joined by ' | ' if multiple.
    """
    temp: Dict[str, Set[str]] = {}
    for en, de in pairs:
        for w in en.split(" | "):
            key = w.strip()
            temp.setdefault(key, set()).add(de)
    return {en: " | ".join(sorted(dset)) for en, dset in temp.items()}


def filter_existing(
    candidates: Dict[str, str],
    existent: Dict[str, str]
) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Compare candidate translations against existing ones.
    Returns (new_entries, updated_entries).
    """
    new_ent: Dict[str, str] = {}
    upd_ent: Dict[str, str] = {}

    for key, val in candidates.items():
        if key not in existent:
            new_ent[key] = val
        else:
            old_set = set(existent[key].split(" | "))
            new_set = set(val.split(" | "))
            if new_set - old_set:
                combined = sorted(old_set | new_set)
                upd_ent[key] = " | ".join(combined)

    return new_ent, upd_ent


def write_lines(
    entries: Dict[str, str],
    prefix: str,
    outpath: Path,
    delimiter: str
) -> None:
    """
    Write out entries as lines of the form:
      {prefix} {key}{delimiter}{value}
    Creates parent dirs if needed.
    """
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with outpath.open("w", encoding="utf-8") as fp:
        for key, val in entries.items():
            fp.write(f"{prefix} {key}{delimiter}{val}\n")


def main() -> None:
    """Main processing pipeline."""
    # 1. Integrity check
    check_data_integrity(InputData.FILEPATH, InputData.DELIMITER)

    # 2. Read & extract DEU → ENG
    deu_raw = read_tuples(InputData.FILEPATH, InputData.DELIMITER, DeuToEng.CATEGORY)
    deu_pairs = extract_deu_to_eng(
        deu_raw,
        DeuToEng.PREFIX_SIMPLE,
        DeuToEng.PREFIX_ARTIKEL_PLURAL
    )
    candidates = build_translation_dict(deu_pairs)

    # 3. Read & extract ENG → DEU
    eng_raw = read_tuples(InputData.FILEPATH, InputData.DELIMITER, EngToDeu.CATEGORY)
    eng_pairs = extract_eng_to_deu(
        eng_raw,
        EngToDeu.PREFIX_SIMPLE
    )
    existing = build_translation_dict(eng_pairs)

    # 4. Filter new vs. updated
    new_entries, updated_entries = filter_existing(candidates, existing)

    # 5. Report
    print("\nNew entries to be added:")
    pp.pprint(new_entries)
    print("\nEntries to be updated:")
    pp.pprint(updated_entries)

    # 6. Write out CSVs
    write_lines(
        new_entries,
        EngToDeu.PREFIX_SIMPLE,
        Path(OutputData.NEW_ENTRIES_FILEPATH),
        OutputData.DELIMITER
    )
    write_lines(
        updated_entries,
        EngToDeu.PREFIX_SIMPLE,
        Path(OutputData.UPDATED_ENTRIES_FILEPATH),
        OutputData.DELIMITER
    )


if __name__ == "__main__":
    main()
