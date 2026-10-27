# roman

Conversión de números enteros a numerales romanos y viceversa, en forma canónica y sustractiva, para el rango 1..3999.

## Requisitos

- Python >= 3.9
- Sin dependencias de terceros en tiempo de ejecución: solo biblioteca estándar (`re`)

## Instalación

```bash
pip install -e .
```

El nombre de distribución es `roman-numerals-lib`; el nombre de importación es `roman`.

## Uso

```python
from roman import to_roman, from_roman

to_roman(1994)         # "MCMXCIV"
to_roman(3999)         # "MMMCMXCIX"
from_roman("iv")       # 4
from_roman("McmXCiv")  # 1994
```

## API

| Función | Firma | Devuelve | Dominio de entrada |
|---|---|---|---|
| `to_roman` | `to_roman(n: int) -> str` | Numeral romano canónico | `n` en 1..3999 |
| `from_roman` | `from_roman(s: str) -> int` | Valor entero | `s` canónico en 1..3999 |

Constantes públicas: `MIN_VALUE` (1), `MAX_VALUE` (3999) y `NUMERAL_TABLE`.

## Excepciones

| Función | Entrada | Excepción | Mensaje |
|---|---|---|---|
| `to_roman` | `True`, `False` | `TypeError` | `to_roman() expects int, got bool` |
| `to_roman` | tipo no `int` (`1.0`, `"1"`, `None`) | `TypeError` | `to_roman() expects int, got <tipo>` |
| `to_roman` | fuera de 1..3999 (`0`, `4000`) | `ValueError` | `to_roman() argument must be in 1..3999, got <n>` |
| `from_roman` | cadena vacía `""` | `ValueError` | `from_roman() argument must not be empty` |
| `from_roman` | no canónica (`"IIII"`, `"VV"`, `"IC"`, `"MMMM"`) | `ValueError` | `from_roman() argument is not a canonical roman numeral: <repr>` |

## Reglas de canonicidad

- Forma sustractiva obligatoria: 4 -> `IV`, 9 -> `IX`, 40 -> `XL`, 90 -> `XC`, 400 -> `CD`, 900 -> `CM`.
- Se rechazan las formas aditivas (`"IIII"`, `"VV"`) y las no canónicas (`"IC"`, `"VIIII"`).
- `from_roman` acepta minúsculas, mayúsculas y mezcla de ambas (`"McmXCiv"`).
- No se aceptan espacios, saltos de línea ni caracteres fuera del alfabeto romano.
- El rango admitido es 1..3999: ni `0` ni `4000` tienen representación canónica.

## Pruebas

```bash
python -m pytest
```

## Alcance

Librería pura de un solo módulo (`src/roman.py`): sin servidor, sin interfaz de línea de comandos, sin persistencia, sin red y sin dependencias de terceros. `to_roman` y `from_roman` son funciones puras y deterministas.
