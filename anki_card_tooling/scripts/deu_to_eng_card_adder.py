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


@dataclasses.dataclass(frozen=True, kw_only=True)
class _TranslationPair:
    deu: str
    eng: str


@dataclasses.dataclass(frozen=True, kw_only=True)
class _Config:
    input_file_delimiter: str
    input_filepath: pathlib.Path
    output_file_delimiter: str
    output_filepath: pathlib.Path


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


def _split_strict(s: str, *, delimiter: str) -> typing.Generator[str]:
    for part in s.split(delimiter):
        if s != s.strip():
            raise ValueError(f"String=`{s}` has leading or trailing whitespace")
        yield part


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
                eng_words_part, deu_word, _ = _split_strict(
                    card.back, delimiter=", "
                )  # TODO: HERE
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
    output_file_delimiter: str,
    output_filepath: pathlib.Path,
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

    if not unique_deu_to_eng_pairs_by_eng:
        print("[INFO] No unique deu_to_eng_pairs found, translations are up-to-date.")
        return

    with output_filepath.open("w", encoding="utf-8") as fp:
        for eng_word, deu_eng_pairs in unique_deu_to_eng_pairs_by_eng.items():
            all_pairs_per_eng_word = deu_eng_pairs + eng_to_eng_deu_pairs.get(
                eng_word, []
            )
            deu_words = " | ".join(
                sorted({pair.deu for pair in all_pairs_per_eng_word})
            )
            fp.write(
                f"{_CardCategory.ENG_TO_DEU}: {eng_word}{output_file_delimiter}{deu_words}\n"
            )


def run_deu_to_eng_card_adder() -> None:
    config = _Config(
        input_file_delimiter="\t",
        input_filepath=pathlib.Path("input_deck/Deutsche Übung.txt"),
        output_file_delimiter=";",
        output_filepath=pathlib.Path("output/upserted_translations.csv"),
    )
    with config.input_filepath.open("r", encoding="utf-8") as fp:
        raw_rows = list(csv.reader(fp, delimiter=config.input_file_delimiter))

    anki_cards: list[_AnkiCard] = _fetch_cards(raw_rows=raw_rows)
    deu_to_eng_pairs: list[_TranslationPair] = _fetch_deu_to_eng_pairs(cards=anki_cards)
    eng_to_deu_pairs: list[_TranslationPair] = _fetch_eng_to_deu_pairs(cards=anki_cards)

    if eng_to_deu_pairs_unique := set(eng_to_deu_pairs).difference(deu_to_eng_pairs):
        formatted = pprint.pformat(eng_to_deu_pairs_unique)
        breakpoint()
        raise ValueError(
            f"There are ENG to DEU but not DEU to ENG translations:\n{formatted}"
        )

    _write_upserted_translation_pairs(
        output_file_delimiter=config.output_file_delimiter,
        output_filepath=config.output_filepath,
        deu_to_eng_pairs=deu_to_eng_pairs,
        eng_to_deu_pairs=eng_to_deu_pairs,
    )


if __name__ == "__main__":
    run_deu_to_eng_card_adder()
