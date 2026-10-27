"""Conversión de números enteros a numerales romanos y viceversa.

Librería pequeña sin dependencias externas: solo usa `re` de la biblioteca
estándar. Expone dos funciones públicas, `to_roman` y `from_roman`, que trabajan
únicamente con el rango canónico 1..3999 y con la forma sustractiva.
"""

import re

# Límites del dominio numeral romano.
MIN_VALUE: int = 1
MAX_VALUE: int = 3999

# Pares (valor, numeral) ordenados de forma descendente. Los pares sustractivos
# (CM, CD, XC, XL, IX, IV) son la única representación admitida para 900, 400,
# 90, 40, 9 y 4 respectivamente.
NUMERAL_TABLE: tuple[tuple[int, str], ...] = (
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
)

# Patrón de la forma canónica, sin anclas ^ ni $: la validación se hace con
# `fullmatch`, de modo que una entrada con salto de línea final ("IV\n") se
# rechaza en lugar de aceptarse.
CANONICAL_PATTERN: str = r"M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})"
CANONICAL_RE: re.Pattern[str] = re.compile(CANONICAL_PATTERN)

__all__: list[str] = ["to_roman", "from_roman", "MIN_VALUE", "MAX_VALUE"]


def to_roman(n: int) -> str:
    """Convierte un entero de 1..3999 a su numeral romano canónico.

    Args:
        n: Entero a convertir. Los valores `bool` se rechazan.

    Returns:
        str: Numeral romano canónico de `n`, en forma sustractiva.

    Raises:
        TypeError: Si `n` no es un `int` (`bool` incluido, por ser subclase).
        ValueError: Si `n` está fuera del rango `MIN_VALUE..MAX_VALUE` (1..3999).
    """
    # `bool` hereda de `int`, por eso se descarta antes que el tipo general.
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError(f"to_roman() expects int, got {type(n).__name__}")

    if not MIN_VALUE <= n <= MAX_VALUE:
        raise ValueError(f"to_roman() argument must be in 1..3999, got {n}")

    # Sustracción voraz sobre la tabla: cada fila aporta su numeral repetido
    # tantas veces como cabe en el resto.
    parts: list[str] = []
    remainder = n
    for value, numeral in NUMERAL_TABLE:
        count, remainder = divmod(remainder, value)
        if count > 0:
            parts.append(numeral * count)

    return "".join(parts)


def from_roman(s: str) -> int:
    """Convierte un numeral romano canónico en el entero correspondiente.

    Acepta mayúsculas, minúsculas y combinación de ambas.

    Args:
        s: Numeral romano a convertir.

    Returns:
        int: Valor entero del numeral, comprendido entre `MIN_VALUE` y `MAX_VALUE`.

    Raises:
        ValueError: Si `s` está vacía o no es un numeral romano canónico
            (por ejemplo "IIII", "VV", "IC" o "MMMM").
    """
    if not s:
        raise ValueError("from_roman() argument must not be empty")

    # La normalización a mayúsculas es lo que permite aceptar minúsculas.
    upper = s.upper()
    if CANONICAL_RE.fullmatch(upper) is None:
        raise ValueError(f"from_roman() argument is not a canonical roman numeral: {s!r}")

    # Lectura de izquierda a derecha: en cada fila de la tabla se consumen los
    # prefijos repetidos del numeral desde la posición actual.
    result = 0
    cursor = 0
    for value, numeral in NUMERAL_TABLE:
        while upper.startswith(numeral, cursor):
            result += value
            cursor += len(numeral)

    # Segunda puerta de seguridad: la re-codificación debe coincidir con la
    # entrada, así ninguna forma no canónica puede colarse aunque el patrón
    # se relajara en el futuro.
    if to_roman(result) != upper:
        raise ValueError(f"from_roman() argument is not a canonical roman numeral: {s!r}")

    return result
