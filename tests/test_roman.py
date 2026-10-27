"""Suite de pruebas de la librería `roman`.

Cubre los valores conocidos, los contratos de error y el roundtrip completo del
rango 1..3999. Los errores se verifican por su tipo de excepción, nunca por su
mensaje, para no acoplar las pruebas a la redacción de los mensajes.
"""

import pytest

from roman import to_roman, from_roman, MIN_VALUE, MAX_VALUE, NUMERAL_TABLE

# Tabla de valores conocidos: (entero, numeral canónico).
KNOWN_VALUES: tuple[tuple[int, str], ...] = (
    (1, "I"),
    (2, "II"),
    (3, "III"),
    (4, "IV"),
    (5, "V"),
    (9, "IX"),
    (10, "X"),
    (14, "XIV"),
    (40, "XL"),
    (44, "XLIV"),
    (50, "L"),
    (90, "XC"),
    (99, "XCIX"),
    (100, "C"),
    (400, "CD"),
    (444, "CDXLIV"),
    (500, "D"),
    (900, "CM"),
    (944, "CMXLIV"),
    (1000, "M"),
    (1666, "MDCLXVI"),
    (1994, "MCMXCIV"),
    (2024, "MMXXIV"),
    (3999, "MMMCMXCIX"),
)

# La misma tabla en orden inverso: (numeral, entero).
KNOWN_NUMERALS: tuple[tuple[str, int], ...] = tuple(
    (numeral, value) for value, numeral in KNOWN_VALUES
)


@pytest.mark.parametrize(("value", "numeral"), KNOWN_VALUES)
def test_to_roman_known_values(value: int, numeral: str) -> None:
    assert to_roman(value) == numeral


def test_to_roman_lower_bound() -> None:
    assert to_roman(1) == "I"


def test_to_roman_upper_bound() -> None:
    assert to_roman(3999) == "MMMCMXCIX"


@pytest.mark.parametrize("value", [1, 4, 9, 40, 90, 400, 900, 1994, 2024, 3999])
def test_to_roman_returns_str(value: int) -> None:
    assert isinstance(to_roman(value), str)


@pytest.mark.parametrize(
    ("value", "numeral"),
    (
        (4, "IV"),
        (9, "IX"),
        (40, "XL"),
        (90, "XC"),
        (400, "CD"),
        (900, "CM"),
    ),
)
def test_to_roman_subtractive_forms(value: int, numeral: str) -> None:
    assert to_roman(value) == numeral


@pytest.mark.parametrize("value", [True, False])
def test_to_roman_rejects_bool(value: bool) -> None:
    with pytest.raises(TypeError):
        to_roman(value)


@pytest.mark.parametrize("value", [1.0, "1", None, [1], 3 + 0j])
def test_to_roman_rejects_non_int(value: object) -> None:
    with pytest.raises(TypeError):
        to_roman(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [0, -1, -3999])
def test_to_roman_rejects_below_range(value: int) -> None:
    with pytest.raises(ValueError):
        to_roman(value)


@pytest.mark.parametrize("value", [4000, 4001, 10**6])
def test_to_roman_rejects_above_range(value: int) -> None:
    with pytest.raises(ValueError):
        to_roman(value)


@pytest.mark.parametrize(("numeral", "value"), KNOWN_NUMERALS)
def test_from_roman_known_values(numeral: str, value: int) -> None:
    assert from_roman(numeral) == value


@pytest.mark.parametrize(
    ("numeral", "value"),
    (("iv", 4), ("mmmcmxcix", 3999), ("mcmxciv", 1994)),
)
def test_from_roman_accepts_lowercase(numeral: str, value: int) -> None:
    assert from_roman(numeral) == value


@pytest.mark.parametrize(
    ("numeral", "value"),
    (("McmXCiv", 1994), ("iV", 4)),
)
def test_from_roman_accepts_mixed_case(numeral: str, value: int) -> None:
    assert from_roman(numeral) == value


def test_from_roman_returns_int() -> None:
    result = from_roman("X")
    assert isinstance(result, int)
    assert not isinstance(result, bool)


def test_from_roman_rejects_empty() -> None:
    with pytest.raises(ValueError):
        from_roman("")


@pytest.mark.parametrize("numeral", ["IIII", "VV", "IC", "MMMM"])
def test_from_roman_rejects_non_canonical(numeral: str) -> None:
    with pytest.raises(ValueError):
        from_roman(numeral)


@pytest.mark.parametrize(
    "numeral",
    ["IL", "VX", "XXXX", "LC", "DM", "VIIII", "CCCC", "DD", "XM", "IIX"],
)
def test_from_roman_rejects_other_non_canonical(numeral: str) -> None:
    with pytest.raises(ValueError):
        from_roman(numeral)


@pytest.mark.parametrize(
    "numeral",
    [
        "ABC",
        "IV ",
        " IV",
        "IV\n",
        "I I",
        "Ⅳ",
    ],
)
def test_from_roman_rejects_invalid_characters(numeral: str) -> None:
    with pytest.raises(ValueError):
        from_roman(numeral)


@pytest.mark.parametrize("value", range(MIN_VALUE, MAX_VALUE + 1))
def test_roundtrip_1_to_3999(value: int) -> None:
    assert from_roman(to_roman(value)) == value


def test_roundtrip_all_canonical_strings() -> None:
    for value in range(MIN_VALUE, MAX_VALUE + 1):
        numeral = to_roman(value)
        assert to_roman(from_roman(numeral)) == numeral


def test_constants() -> None:
    assert MIN_VALUE == 1
    assert MAX_VALUE == 3999
    assert len(NUMERAL_TABLE) == 13
