import collections
import csv
import dataclasses
import enum
import functools
import pathlib
import pprint
import re
import typing

import pydantic


class _MetadataTag(enum.StrEnum):
    SEPARATOR = "#separator:"
    HTML = "#html:"
    TAGS_COLUMN = "#tags column:"


class _CardCategory(enum.StrEnum):
    ABKUERZUNG = "ABKÜRZUNG"
    ADJEKTIVDEKLINATION_AKK_BESTIMMT = (
        "ADJEKTIVDEKLINATION und AKKUSATIV mit BESTIMMTEM ARTIKEL (der/die/das)"
    )
    ADJEKTIVDEKLINATION_AKK_NEGATIV = (
        "ADJEKTIVDEKLINATION und AKKUSATIV mit NEGATIVEM ARTIKEL (kein)"
    )
    ADJEKTIVDEKLINATION_AKK_POSSESSIV = (
        "ADJEKTIVDEKLINATION und AKKUSATIV mit POSSESSIVARTIKEL (mein)"
    )
    ADJEKTIVDEKLINATION_AKK_UNBESTIMMT = (
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
    PRAEPOSITION_AKK_DATIV = "PRÄPOSITION ⋀ AKKUSATIV/DATIV"
    PRAETERITUM_HAT_IST_PERFEKT = "PRÄTERITUM ⋀ HAT/IST + PERFEKT"
    QUIZFRAGE = "QUIZFRAGE"
    REFLEXIVES_VERB_AKK_DATIV = "REFLEXIVES VERB ⋀ AKKUSATIV/DATIV"
    REFLEXIVPRONOMEN_DATIV = "REFLEXIVPRONOMEN ⋀ DATIV"
    SUFFIX_ARTIKEL_MIT_AUSNAHMEN = "SUFFIX-ARTIKEL (MIT AUSNAHMEN)"
    TEMPORALE_PRAEPOSITION_BEDEUTUNG = "TEMPORALE PRÄPOSITION BEDEUTUNG"


class _AnkiCard(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    front: str = pydantic.Field(..., pattern=r"^\S[^:]*: [^:]*\S$")
    back: str = pydantic.Field(..., pattern=r"^\S.*\S$")

    @classmethod
    def parse_iterable(cls, iterable: typing.Iterable) -> typing.Self:
        return cls.model_validate(
            dict(zip(cls.model_fields.keys(), iterable, strict=True))
        )

    @functools.cached_property
    def _split_front(self) -> list[str]:
        return self.front.split(": ")

    @functools.cached_property
    def category(self) -> _CardCategory:
        card_category_str, front_without_category = self._split_front
        return _CardCategory(card_category_str)

    @functools.cached_property
    def front_without_category(self) -> str:
        _, front_without_category = self._split_front
        return front_without_category


def _fetch_cards(*, raw_rows: list[list[str]]) -> list[_AnkiCard]:
    ignored_rows: list[list[str]] = []
    anki_cards: list[_AnkiCard] = []
    html_char_pattern: re.Pattern[str] = re.compile(r"&\w+;")
    for row in raw_rows:
        if not row[-1]:
            row.pop()
        if any(html_char_pattern.search(row_part) for row_part in row):
            raise ValueError(f"[ERROR] HTML character found in `{row=}`")
        row_first_part, *_ = row
        if any(row_first_part.startswith(pref) for pref in _MetadataTag):
            print(f"[WARN] Skipping metadata {row=}")
            ignored_rows.append(row)
            continue
        try:
            anki_card: _AnkiCard = _AnkiCard.parse_iterable(row)
        except (pydantic.ValidationError, ValueError) as err:
            raise ValueError(f"[ERROR] Validation error in `{row=}`") from err

        anki_cards.append(anki_card)

    print(f"[INFO] Ignored `{len(ignored_rows)}` rows.")
    print(f"[INFO] Collected `{len(anki_cards)}` cards.")
    anki_card_categories: list[_CardCategory] = [ac.category for ac in anki_cards]
    print(f"[INFO] Collected `{len(set(anki_card_categories))}` categories.")
    return anki_cards


#: Mapping of HTML entities to their literal replacements
HTML_CATEGORY_TO_REAL_SYMBOL: dict[str, str] = {
    "&#x27;": "'",
    "&quot;": '"',
    "&amp;": "&",
    "&nbsp;": " ",
    "&gt;": ">",
}

NO_SINGULAR_TAG = "NO SINGULAR"


@dataclasses.dataclass(frozen=True, kw_only=True)
class _InputConfig:
    delimiter: str
    filepath: pathlib.Path

    @functools.cached_property
    def filename(self):
        return self.filepath.stem


@dataclasses.dataclass(frozen=True, kw_only=True)
class _OutputConfig:
    delimiter: str
    upserted_entries_filepath: pathlib.Path


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


pp: pprint.PrettyPrinter = pprint.PrettyPrinter(indent=4)  # TODO: DELL


def check_data_integrity(filepath: pathlib.Path, delimiter: str) -> None:
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


def read_tuples(
    filepath: pathlib.Path, delimiter: str, category: str
) -> list[tuple[str, str]]:
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
    entries: dict[str, str], prefix: str, outpath: pathlib.Path, delimiter: str
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


def main(input_config: _InputConfig) -> None:
    """Main processing pipeline."""
    # 1. Integrity check
    check_data_integrity(input_config.filepath, input_config.delimiter)

    # 2. Read & extract DEU → ENG
    deu_raw = read_tuples(input_config.filepath, input_config.delimiter, "DEU → ENG")
    breakpoint()
    print("gdg")
    deu_pairs = extract_deu_to_eng(
        deu_raw, "DEU → ENG:", DeuToEng.PREFIX_ARTIKEL_PLURAL
    )
    candidates = build_translation_dict(deu_pairs)

    # 3. Read & extract ENG → DEU
    eng_raw = read_tuples(
        _InputConfig.filepath, _InputConfig.delimiter, EngToDeu.CATEGORY
    )
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
        pathlib.Path(_OutputConfig.new_entries_filepath),
        _OutputConfig.delimiter,
    )
    write_lines(
        updated_entries,
        EngToDeu.PREFIX_SIMPLE,
        pathlib.Path(_OutputConfig.updated_entries_filepath),
        _OutputConfig.delimiter,
    )


def _split_strict(s: str, *, delimiter: str) -> typing.Generator[str]:
    for part in s.split(delimiter):
        if s != s.strip():
            raise ValueError(f"String=`{s}` has leading or trailing whitespace")
        yield part


@dataclasses.dataclass(frozen=True, kw_only=True)
class _TranslationPair:
    deu: str
    eng: str


def _fetch_deu_to_eng_pairs(*, cards: list[_AnkiCard]) -> list[_TranslationPair]:
    deu_to_eng_pairs: list[_TranslationPair] = []
    for card in cards:
        match card.category:
            case _CardCategory.DEU_TO_ENG:
                deu_word: str = card.front_without_category
                for eng_word in _split_strict(card.back, delimiter=" | "):
                    pair = _TranslationPair(deu=deu_word, eng=eng_word)
                    deu_to_eng_pairs.append(pair)
            case _CardCategory.DEU_TO_ENG_ARTIKEL_PLURAL:
                eng_words_part, deu_word, _ = _split_strict(card.back, delimiter=", ")
                for eng_word in _split_strict(eng_words_part, delimiter=" | "):
                    pair = _TranslationPair(deu=deu_word, eng=eng_word)
                    deu_to_eng_pairs.append(pair)
    return deu_to_eng_pairs


def _fetch_eng_to_deu_pairs(*, cards: list[_AnkiCard]) -> list[_TranslationPair]:
    eng_to_deu_pairs: list[_TranslationPair] = []
    for card in cards:
        match card.category:
            case _CardCategory.ENG_TO_DEU:
                eng_word: str = card.front_without_category
                for deu_word in _split_strict(card.back, delimiter=" | "):
                    pair = _TranslationPair(deu=deu_word, eng=eng_word)
                    eng_to_deu_pairs.append(pair)
    return eng_to_deu_pairs


def _group_pairs_by_eng_word(
    *,
    pairs: list[_TranslationPair],
) -> dict[str, list[_TranslationPair]]:
    pairs_by_eng: dict[str, list[_TranslationPair]] = collections.defaultdict(list)
    for pair in pairs:
        pairs_by_eng[pair.eng].append(pair)
    return pairs_by_eng


def _write_upserted_translation_pairs(
    *,
    output_config: _OutputConfig,
    deu_to_eng_pairs: list[_TranslationPair],
    eng_to_deu_pairs: list[_TranslationPair],
) -> None:
    unique_deu_to_eng_pairs: list[_TranslationPair] = sorted(
        set(deu_to_eng_pairs).difference(eng_to_deu_pairs), key=lambda x: x.eng
    )

    unique_deu_to_eng_pairs_by_eng: dict[str, list[_TranslationPair]] = (
        _group_pairs_by_eng_word(pairs=unique_deu_to_eng_pairs)
    )

    eng_to_eng_deu_pairs: dict[str, list[_TranslationPair]] = _group_pairs_by_eng_word(
        pairs=eng_to_deu_pairs
    )

    with output_config.upserted_entries_filepath.open("w", encoding="utf-8") as fp:
        for eng_word, deu_eng_pairs in unique_deu_to_eng_pairs_by_eng.items():
            all_pairs_per_eng_word = deu_eng_pairs + eng_to_eng_deu_pairs.get(
                eng_word, []
            )
            deu_words = " | ".join(
                sorted({pair.deu for pair in all_pairs_per_eng_word})
            )
            built_line = f"{_CardCategory.ENG_TO_DEU}: {eng_word}{output_config.delimiter}{deu_words}"
            fp.write(built_line + "\n")


def main_new() -> None:
    input_config = _InputConfig(
        filepath=pathlib.Path("input_deck/Deutsche Übung.txt"), delimiter="\t"
    )
    with input_config.filepath.open("r", encoding="utf-8") as fp:
        raw_rows = list(csv.reader(fp, delimiter=input_config.delimiter))

    anki_cards: list[_AnkiCard] = _fetch_cards(raw_rows=raw_rows)
    deu_to_eng_pairs: list[_TranslationPair] = _fetch_deu_to_eng_pairs(cards=anki_cards)
    eng_to_deu_pairs: list[_TranslationPair] = _fetch_eng_to_deu_pairs(cards=anki_cards)

    if eng_to_deu_pairs_unique := set(eng_to_deu_pairs).difference(deu_to_eng_pairs):
        formatted = pprint.pformat(eng_to_deu_pairs_unique)
        raise ValueError(
            f"For these cards there are ENG to DEU but not DEU to ENG translations:\n{formatted}"
        )

    _write_upserted_translation_pairs(
        output_config=_OutputConfig(
            delimiter=";",
            upserted_entries_filepath=pathlib.Path("output/upserted_translations.csv"),
        ),
        deu_to_eng_pairs=deu_to_eng_pairs,
        eng_to_deu_pairs=eng_to_deu_pairs,
    )


if __name__ == "__main__":
    main_new()
