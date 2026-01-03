import csv
import dataclasses
import enum
import pathlib
import pprint
import re
import typing
from pathlib import Path
from typing import Pattern

import pydantic
from typing_extensions import Literal



class _MetadataTag(enum.StrEnum):
    SEPARATOR = "#separator:"
    HTML = "#html:"
    TAGS_COLUMN = "#tags column:"


class _CardCategory(enum.StrEnum):
    ABKUERZUNG = "ABKÜRZUNG"
    ADJEKTIVDEKLINATION_AKKUSATIV_BESTIMMT = (
        "ADJEKTIVDEKLINATION und AKKUSATIV mit BESTIMMTEM ARTIKEL (der/die/das)"
    )
    ADJEKTIVDEKLINATION_AKKUSATIV_NEGATIV = (
        "ADJEKTIVDEKLINATION und AKKUSATIV mit NEGATIVEM ARTIKEL (kein)"
    )
    ADJEKTIVDEKLINATION_AKKUSATIV_POSSESSIV = (
        "ADJEKTIVDEKLINATION und AKKUSATIV mit POSSESSIVARTIKEL (mein)"
    )
    ADJEKTIVDEKLINATION_AKKUSATIV_UNBESTIMMT = (
        "ADJEKTIVDEKLINATION und AKKUSATIV mit UNBESTIMMTEM ARTIKEL (ein)"
    )
    ADJEKTIVDEKLINATION_DATIV_BESTIMMT = (
        "ADJEKTIVDEKLINATION und DATIV mit BESTIMMTEM ARTIKEL (der/die/das)"
    )
    ADJEKTIVDEKLINATION_DATIV_NEGATIV = (
        "ADJEKTIVDEKLINATION und DATIV mit NEGATIVEM ARTIKEL (kein)"
    )
    ADJEKTIVDEKLINATION_DATIV_POSSESSIV = (
        "ADJEKTIVDEKLINATION und DATIV mit POSSESSIVARTIKEL (mein)"
    )
    ADJEKTIVDEKLINATION_DATIV_UNBESTIMMT = (
        "ADJEKTIVDEKLINATION und DATIV mit UNBESTIMMTEM ARTIKEL (ein)"
    )
    ADJEKTIVDEKLINATION_NOMINATIV_BESTIMMT = (
        "ADJEKTIVDEKLINATION und NOMINATIV mit BESTIMMTEM ARTIKEL (der/die/das)"
    )
    ADJEKTIVDEKLINATION_NOMINATIV_NEGATIV = (
        "ADJEKTIVDEKLINATION und NOMINATIV mit NEGATIVEM ARTIKEL (kein)"
    )
    ADJEKTIVDEKLINATION_NOMINATIV_POSSESSIV = (
        "ADJEKTIVDEKLINATION und NOMINATIV mit POSSESSIVARTIKEL (mein)"
    )
    ADJEKTIVDEKLINATION_NOMINATIV_UNBESTIMMT = (
        "ADJEKTIVDEKLINATION und NOMINATIV mit UNBESTIMMTEM ARTIKEL (ein)"
    )
    AKKUSATIV_DATIV_KONJUGATION = "AKKUSATIV/DATIV KONJUGATION"
    AKKUSATIVFORM = "AKKUSATIVFORM"
    ARTIKEL_PLURAL = "ARTIKEL ⋀ PLURAL"
    AUF_DEUTSCH = "AUF DEUTSCH"
    AUFFORDERUNG = "AUFFORDERUNG"
    DATIVFORM = "DATIVFORM"
    DEU_TO_ENG = "DEU → ENG"
    DEU_TO_ENG_ARTIKEL_PLURAL = "DEU → ENG ⋀ ARTIKEL ⋀ PLURAL"
    ENG_TO_DEU = "ENG → DEU"
    GENITIV_TRANSFORMATION = "GENITIV TRANSFORMATION"
    HAT_IST_PERFEKT = "HAT/IST + PERFEKT"
    IMPERATIV_DU_FORM = "IMPERATIV DU‑FORM"
    IMPERATIV_IHR_FORM = "IMPERATIV IHR‑FORM"
    KOMPARATIV_SUPERLATIV = "KOMPARATIV ⋀ SUPERLATIV"
    KONJUGATION_ICH_DU_ES = "KONJUGATION (ICH/DU/ES)"
    KONJUGATION_WIR_IHR_SIE = "KONJUGATION (WIR/IHR/SIE)"
    LOKALE_PRAEPOSITION_BEDEUTUNG = "LOKALE PRÄPOSITION BEDEUTUNG"
    PRAEPOSITION_AKKUSATIV_DATIV = "PRÄPOSITION ⋀ AKKUSATIV/DATIV"
    PRAETERITUM_HAT_IST_PERFEKT = "PRÄTERITUM ⋀ HAT/IST + PERFEKT"
    QUIZFRAGE = "QUIZFRAGE"
    REFLEXIVES_VERB_AKKUSATIV_DATIV = "REFLEXIVES VERB ⋀ AKKUSATIV/DATIV"
    REFLEXIVPRONOMEN_DATIV = "REFLEXIVPRONOMEN ⋀ DATIV"
    SUFFIX_ARTIKEL_MIT_AUSNAHMEN = "SUFFIX-ARTIKEL (MIT AUSNAHMEN)"
    TEMPORALE_PRAEPOSITION_BEDEUTUNG = "TEMPORALE PRÄPOSITION BEDEUTUNG"


class _RawCard(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    front: str = pydantic.Field(..., pattern=r"^[^:]+: [^:]+$")
    back: str

    @classmethod
    def parse_iterable(cls, iterable: typing.Iterable) -> typing.Self:
        return cls.model_validate(
            dict(zip(cls.model_fields.keys(), iterable, strict=True))
        )


def foo(*, filepath: pathlib.Path, delimiter: str):
    ignored_rows: list[list[str]] = []
    raw_cards: list[_RawCard] = []
    with filepath.open("r", encoding="utf-8") as fp:
        for row in csv.reader(fp, delimiter=delimiter):
            row_first_part, *_ = row
            if any(row_first_part.startswith(pref) for pref in list(_MetadataTag)):
                print(f"[WARN] Skipping metadata {row=}")
                ignored_rows.append(row)
                continue
            if not row[-1]:
                row.pop()
            # if any( (row_part in HTML_CATEGORY_TO_REAL_SYMBOL) for row_part in row): # TODO: TMPP

            try:
                raw_card: _RawCard = _RawCard.parse_iterable(row)
            except (pydantic.ValidationError, ValueError) as err:
                raise ValueError(f"[ERROR] Validation error in `{row=}`") from err

            raw_cards.append(raw_card)
    for raw_card in raw_cards:
        card_category_str, front_key = raw_card.front.split(": ")
        card_category = _CardCategory(card_category_str)
        print(card_category)
    set([rc.front.split(": ")[0] for rc in raw_cards])
    breakpoint()

    print(f"[INFO] Ignored `{len(ignored_rows)}` rows.")
    print(f"[INFO] Collected `{len(raw_cards)}` cards.")
    breakpoint()
    print("ag")


#: Mapping of HTML entities to their literal replacements
HTML_CATEGORY_TO_REAL_SYMBOL: Final[dict[str, str]] = {
    "&#x27;": "'",
    "&quot;": '"',
    "&amp;": "&",
    "&nbsp;": " ",
    "&gt;": ">",
}

NO_SINGULAR_TAG = "NO SINGULAR"


@dataclasses.dataclass(frozen=True, kw_only=True)
class _InputData:
    """Input deck configuration."""

    FILEPATH: Final[Path] = Path("input_deck") / "Deutsche Übung.txt"
    FILENAME = FILEPATH.stem
    DELIMITER: Final[Literal["\t"]] = "\t"


@dataclasses.dataclass(frozen=True, kw_only=True)
class _OutputData:
    """Output files and directories."""

    DELIMITER: typing.Literal[";"] = ";"
    PARENT_DIR: Path = Path("output")
    NEW_ENTRIES_FILEPATH = f"{PARENT_DIR}/new_translations.csv"
    UPDATED_ENTRIES_FILEPATH = f"{PARENT_DIR}/updated_translations.csv"


@dataclasses.dataclass(frozen=True, kw_only=True)
class _Config:
    input_data: _InputData
    output_data: _OutputData


@dataclasses.dataclass(frozen=True, kw_only=True)
class DeuToEng:
    """German→English tags in the deck."""

    CATEGORY = "DEU → ENG"
    PREFIX_SIMPLE = f"{CATEGORY}:"
    PREFIX_ARTIKEL_PLURAL = f"{CATEGORY} ⋀ ARTIKEL ⋀ PLURAL:"


@dataclasses.dataclass(frozen=True, kw_only=True)
class EngToDeu:
    """English→German tags in the deck."""

    CATEGORY = "ENG → DEU"
    PREFIX_SIMPLE = f"{CATEGORY}:"


pp: Final[pprint.PrettyPrinter] = pprint.PrettyPrinter(indent=4)  # TODO: DELL


def check_data_integrity(filepath: Path, delimiter: str) -> None:
    """
    Verify that the first two columns of the TSV do not contain empty values
    or HTML-entity patterns like &...; (except in the #separator/html/tags lines).
    Raises ValueError if any offending rows are found.
    """
    pattern: Pattern[str] = re.compile(r"&\w+;")
    offending: list[list[str]] = []

    with filepath.open("r", encoding="utf-8") as fp:
        reader = csv.reader(fp, delimiter=delimiter)
        for row in reader:
            if any(
                row[0].startswith(pref)
                for pref in ("#separator:", "#html:", "#tags column:")
            ):
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
        for src, tgt in HTML_CATEGORY_TO_REAL_SYMBOL.items():
            print(f"\t{src} -> {tgt}")
        raise ValueError(
            "Dataset contains invalid HTML entities or empty first-two columns."
        )


def read_tuples(filepath: Path, delimiter: str, category: str) -> list[tuple[str, str]]:
    """
    Read all rows containing `category` in the first column, returning a list of
    (category, value) tuples (first two columns only, value stripped).
    """
    out: list[tuple[str, str]] = []
    with filepath.open("r", encoding="utf-8") as fp:
        reader = csv.reader(fp, delimiter=delimiter)
        for row in reader:
            if category in row[0]:
                out.append((row[0], row[1].strip()))
    return out


def extract_deu_to_eng(
    data: list[tuple[str, str]], prefix_simple: str, prefix_artikel_plural: str
) -> list[tuple[str, str]]:
    """
    From raw DEU → ENG rows, extract (english, german) tuples.
    Handles normal entries and 'Artikel ⋀ Plural' entries.
    """
    out: list[tuple[str, str]] = []
    for cat, val in data:
        if cat.startswith(prefix_simple):
            de_word = cat[len(prefix_simple) :].strip()
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
    data: list[tuple[str, str]], prefix_simple: str
) -> list[tuple[str, str]]:
    """
    From raw ENG → DEU rows, extract (english, german) tuples.
    """
    out: list[tuple[str, str]] = []
    for cat, val in data:
        if cat.startswith(prefix_simple):
            en_word = cat[len(prefix_simple) :].strip()
            de_word = val
        else:
            raise ValueError(f"Unexpected category in row: {cat!r}")
        out.append((en_word, de_word))
    return out


def build_translation_dict(pairs: list[tuple[str, str]]) -> dict[str, str]:
    """
    Build a dict mapping each English word (or phrase) to its German translations,
    joined by ' | ' if multiple.
    """
    temp: dict[str, set[str]] = {}
    for en, de in pairs:
        for w in en.split(" | "):
            key = w.strip()
            temp.setdefault(key, set()).add(de)
    return {en: " | ".join(sorted(dset)) for en, dset in temp.items()}


def filter_existing(
    candidates: dict[str, str], existent: dict[str, str]
) -> tuple[dict[str, str], dict[str, str]]:
    """
    Compare candidate translations against existing ones.
    Returns (new_entries, updated_entries).
    """
    new_ent: dict[str, str] = {}
    upd_ent: dict[str, str] = {}

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
    entries: dict[str, str], prefix: str, outpath: Path, delimiter: str
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
    check_data_integrity(_InputData.FILEPATH, _InputData.DELIMITER)

    # 2. Read & extract DEU → ENG
    deu_raw = read_tuples(_InputData.FILEPATH, _InputData.DELIMITER, DeuToEng.CATEGORY)
    deu_pairs = extract_deu_to_eng(
        deu_raw, DeuToEng.PREFIX_SIMPLE, DeuToEng.PREFIX_ARTIKEL_PLURAL
    )
    candidates = build_translation_dict(deu_pairs)

    # 3. Read & extract ENG → DEU
    eng_raw = read_tuples(_InputData.FILEPATH, _InputData.DELIMITER, EngToDeu.CATEGORY)
    eng_pairs = extract_eng_to_deu(eng_raw, EngToDeu.PREFIX_SIMPLE)
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
        Path(_OutputData.NEW_ENTRIES_FILEPATH),
        _OutputData.DELIMITER,
    )
    write_lines(
        updated_entries,
        EngToDeu.PREFIX_SIMPLE,
        Path(_OutputData.UPDATED_ENTRIES_FILEPATH),
        _OutputData.DELIMITER,
    )


def main_new() -> None:
    DELIMITER = "\t"  # TODO: MOVE

    foo(filepath=pathlib.Path("input_deck/Deutsche Übung.txt"), delimiter=DELIMITER)
    breakpoint()
    print("aga")


if __name__ == "__main__":
    main_new()
    # main()
