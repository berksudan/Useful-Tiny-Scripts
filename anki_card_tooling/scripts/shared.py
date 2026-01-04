import enum
import functools
import typing

import pydantic


class CardCategory(enum.StrEnum):
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


class ColorCode(enum.StrEnum):
    BACK_CYAN = "\x1b[46m"
    BACK_YELLOW = "\x1b[43m"
    FORE_BLACK = "\x1b[30m"
    FORE_MAGENTA = "\x1b[35m"
    FORE_RED = "\x1b[31m"
    FORE_YELLOW = "\x1b[33m"
    STYLE_RESET_ALL = "\x1b[0m"

    @classmethod
    def block(cls, *codes: ColorCode, text: str) -> str:
        concatenated_codes = "".join(code.value for code in codes)
        return f"{concatenated_codes}{text}{cls.STYLE_RESET_ALL}"


class AnkiCard(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    front: str = pydantic.Field(..., pattern=r"^\S[^:]*: [^:]*\S$")
    back: str = pydantic.Field(..., pattern=r"^\S.*\S$")

    @classmethod
    def parse_iterable(cls, iterable: typing.Iterable) -> typing.Self:
        return cls.model_validate(
            dict(zip(cls.model_fields.keys(), iterable, strict=True))
        )

    @functools.cached_property
    def to_str(self) -> str:
        return f"{self.front};{self.back}"

    @functools.cached_property
    def to_colored_str(self) -> str:
        return ColorCode.block(
            ColorCode.BACK_CYAN, ColorCode.FORE_BLACK, text=self.to_str
        )
