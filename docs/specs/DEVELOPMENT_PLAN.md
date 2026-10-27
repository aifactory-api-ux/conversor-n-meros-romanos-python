# DEVELOPMENT PLAN: Conversor Números Romanos Python (`roman`)

## 1. ARCHITECTURE OVERVIEW

**Naturaleza del proyecto:** librería Python pura (sin servidor, sin interfaz, sin persistencia, sin red). La fuente de verdad es SPEC.md §4, que fija **exactamente cuatro archivos**:

```
project-root/
├── README.md              # Documentación breve: instalación, uso, tabla API, reglas de validación, comando pytest
├── pyproject.toml         # PEP 621 (name=roman-numerals-lib) + [tool.pytest.ini_options] pythonpath=["src"]
├── src/
│   └── roman.py           # Único módulo: MIN_VALUE, MAX_VALUE, NUMERAL_TABLE, CANONICAL_PATTERN,
│                          # CANONICAL_RE, to_roman, from_roman, __all__
└── tests/
    └── test_roman.py      # Suite pytest: valores conocidos, contratos de error, roundtrip 1..3999
```

**Componentes:**

| Componente | Archivo | Responsabilidad |
|---|---|---|
| Empaquetado / configuración de tests | `pyproject.toml` | `setuptools.build_meta`, `package-dir = {"" = "src"}`, `[tool.setuptools.py-modules] roman = "roman"`, `pythonpath = ["src"]`, `testpaths = ["tests"]`, `dependencies = []`, extra `test = ["pytest>=7.0"]` |
| Núcleo de conversión | `src/roman.py` | Constantes del dominio (`MIN_VALUE=1`, `MAX_VALUE=3999`, `NUMERAL_TABLE` con 13 pares descendentes), regex canónica (`CANONICAL_PATTERN` sin `^`/`$`, validada con `.fullmatch`), `to_roman` (sustracción voraz con `divmod`), `from_roman` (normalización `upper()` + regex + re-codificación) |
| Verificación automática | `tests/test_roman.py` | Funciones pytest planas + `@pytest.mark.parametrize`; sin `unittest.TestCase`; solo se asertan tipos de excepción, nunca mensajes |
| Documentación | `README.md` | Descripción, requisito Python ≥3.9, `pip install -e .`, ejemplos de uso, tabla API, tabla de excepciones, reglas de canonicidad, `pytest`, nota "sin dependencias / sin servidor / sin UI" |

**Contratos públicos (importables como `roman`):** `to_roman(n: int) -> str`, `from_roman(s: str) -> int`, `MIN_VALUE`, `MAX_VALUE`, `NUMERAL_TABLE`, `CANONICAL_PATTERN`, `CANONICAL_RE`, `__all__`. Único import interno permitido en `src/roman.py`: `re`.

**Exclusiones explícitas (no se generan):** `Dockerfile`, `docker-compose.yml`, `run.sh`, `.env` / `.env.example`, `docs/`, `backend/`, `frontend/`, `shared/`, `requirements.txt`, migraciones, observabilidad, CI, linters, `mypy`/`ruff`/`black`. El goal dice *"Solo librería estándar, sin servidor ni interfaz"*; por eso **no existe ítem de Infrastructure & Deployment**: el "despliegue" es `pip install -e .` sobre un módulo puro.

**Decisiones de diseño clave:** `bool` se rechaza antes que `int` (subclase); `CANONICAL_RE.fullmatch` en lugar de `match`/`$` para rechazar `"IV\n"`; doble compuerta en `from_roman` (regex + re-codificación con `to_roman(result) == upper`) para que ninguna cadena no canónica sea aceptada; ambas funciones puras, sin estado mutable ni I/O.

## 2. ACCEPTANCE CRITERIA

1. `python -m pytest -q` ejecutado desde la raíz del repositorio finaliza en verde, incluyendo `test_roundtrip_1_to_3999` (3999 casos parametrizados) y `test_roundtrip_all_canonical_strings`.
2. `from roman import to_roman, from_roman, MIN_VALUE, MAX_VALUE` resuelve sin instalar el paquete (gracias a `pythonpath = ["src"]`) y `to_roman(1) == "I"`, `to_roman(4) == "IV"`, `to_roman(1994) == "MCMXCIV"`, `to_roman(3999) == "MMMCMXCIX"`.
3. `to_roman(True)`, `to_roman(False)`, `to_roman(1.0)`, `to_roman("1")`, `to_roman(None)`, `to_roman([1])` y `to_roman(3+0j)` lanzan `TypeError`; `to_roman(0)`, `to_roman(-1)`, `to_roman(-3999)`, `to_roman(4000)` y `to_roman(10**6)` lanzan `ValueError`.
4. `from_roman("")` lanza `ValueError`; `from_roman("IIII")`, `from_roman("VV")`, `from_roman("IC")` y `from_roman("MMMM")` lanzan `ValueError`; `from_roman("iv") == 4`, `from_roman("mmmcmxcix") == 3999` y `from_roman("McmXCiv") == 1994` devuelven `int` dentro de 1..3999.
5. `README.md` documenta instalación, uso de ambas funciones, tabla de la API, tabla de excepciones, reglas de canonicidad y el comando de ejecución de tests en 40–70 líneas.
6. La librería es solo estándar: `src/roman.py` importa únicamente `re`, `pyproject.toml` declara `dependencies = []` y no existe ningún archivo fuera de los cuatro declarados en SPEC.md §4.

## TEAM SCOPE (MANDATORY — PARSED BY THE PIPELINE)

Proyecto ejecutado íntegramente por el agente **Developer** (restricción explícita del intake: *"quiero que lo haga únicamente el agente Developer"*). Un único rol cubre todos los ítems: implementación, pruebas y documentación.

- `role-dev`: agente Developer, único responsable de los cuatro ítems del plan.

## 3. EXECUTABLE ITEMS

### ITEM 1: Foundation — Empaquetado PEP 621 y configuración de pytest (`pyproject.toml`)

**Goal:** Crear el único archivo de configuración del proyecto, que habilita el contrato de importación `from roman import ...` sin instalación y hace la librería consumible como dependencia por el equipo de ingeniería interno. Contenido exacto:

- `[build-system]`: `requires = ["setuptools>=61.0"]`, `build-backend = "setuptools.build_meta"`.
- `[project]`: `name = "roman-numerals-lib"`, `version = "1.0.0"`, `description` breve, `requires-python = ">=3.9"`, `dependencies = []` (sin dependencias de runtime).
- `[project.optional-dependencies]`: `test = ["pytest>=7.0"]` (pytest es dependencia **solo** de test).
- `[tool.setuptools]`: `package-dir = { "" = "src" }`.
- `[tool.setuptools.py-modules]`: `roman = "roman"` (layout de módulo único; **no** se crea `src/__init__.py`).
- `[tool.pytest.ini_options]`: `pythonpath = ["src"]`, `testpaths = ["tests"]`.

Sin variables de entorno, sin secretos, sin URLs ni puertos.

**Files to create:**
- `pyproject.toml` (create) - metadatos PEP 621 (name=roman-numerals-lib, import name=roman, requires-python>=3.9, dependencies=[]) + `[tool.setuptools]` con `package-dir` y `py-modules` + `[tool.pytest.ini_options]` con `pythonpath=["src"]` y `testpaths=["tests"]`

**Tests required:**
- No aplica (archivo de configuración sin lógica). Su verificación es la validación ejecutable de abajo y queda cubierta indirectamente por toda la suite del Item 3, que solo puede importar `roman` si `pythonpath` está bien configurado.

**Dependencies:** None

**Validation:** `python -c "import pathlib, tomllib; d = tomllib.loads(pathlib.Path('pyproject.toml').read_text()); assert d['project']['name'] == 'roman-numerals-lib'; assert d['project']['dependencies'] == []; assert d['tool']['pytest']['ini_options']['pythonpath'] == ['src']; assert d['tool']['pytest']['ini_options']['testpaths'] == ['tests']; assert d['tool']['setuptools']['py-modules'] == {'roman': 'roman'}; print('OK pyproject')"` (alternativa si el intérprete es <3.11: `grep -q 'pythonpath = \["src"\]' pyproject.toml && grep -q 'dependencies = \[\]' pyproject.toml`).

**Role:** role-dev (backend_developer)

### ITEM 2: Núcleo de conversión — `MIN_VALUE`/`MAX_VALUE`/`NUMERAL_TABLE` + `to_roman` y `from_roman` en `src/roman.py`

**Goal:** Implementar el módulo completo de la librería, con anotaciones de tipo, docstrings en las funciones públicas y comentarios en español donde aporten (sin ruido):

1. **Constantes:** `MIN_VALUE: int = 1`, `MAX_VALUE: int = 3999`; `NUMERAL_TABLE: tuple[tuple[int, str], ...]` con 13 pares descendentes `(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),(50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")`; `CANONICAL_PATTERN: str` con valor `r"M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})"` **sin anclas**; `CANONICAL_RE: re.Pattern[str] = re.compile(CANONICAL_PATTERN)`; `__all__: list[str] = ["to_roman", "from_roman", "MIN_VALUE", "MAX_VALUE"]`. Único import: `re`. Prohibido `os.environ`/`os.getenv`/I/O/red.
2. **`to_roman(n: int) -> str`:** (a) `if isinstance(n, bool) or not isinstance(n, int): raise TypeError(...)` — la comprobación de `bool` va **primero** porque `bool` hereda de `int`; (b) `if not MIN_VALUE <= n <= MAX_VALUE: raise ValueError(...)`; (c) sustracción voraz sobre `NUMERAL_TABLE` con `count, remainder = divmod(remainder, value)` y `parts.append(numeral * count)` cuando `count > 0`; (d) `return "".join(parts)`. Mensajes: `"to_roman() expects int, got bool"`, `"to_roman() expects int, got <typename>"`, `"to_roman() argument must be in 1..3999, got <n>"`.
3. **`from_roman(s: str) -> int`:** (a) `if not s: raise ValueError("from_roman() argument must not be empty")`; (b) `upper = s.upper()` (única normalización: sin `strip`, sin trucos de locale); (c) `if CANONICAL_RE.fullmatch(upper) is None: raise ValueError(...)`; (d) parseo izquierda-a-derecha consumiendo prefijos de cada numeral de `NUMERAL_TABLE`; (e) **segunda compuerta**: `if to_roman(result) != upper: raise ValueError(...)` — garantiza el rechazo de `"IIII"`, `"VV"`, `"IC"`, `"MMMM"` y de cualquier otra cadena no canónica incluso si la regex se relajara; (f) `return result`. Mensajes: `"from_roman() argument is not a canonical roman numeral: <repr>"`.
4. Ambas funciones son puras: sin estado global mutable, sin caché, sin aleatoriedad, sin escritura en disco.

**Files to create:**
- `src/roman.py` (create) - constantes del dominio (MIN_VALUE, MAX_VALUE, NUMERAL_TABLE, CANONICAL_PATTERN, CANONICAL_RE, __all__) + `to_roman(n: int) -> str` + `from_roman(s: str) -> int`, con type hints, docstrings y comentarios en español; import único `re`

**Tests required:**
- La cobertura unitaria de este módulo se entrega en el Item 3 (`tests/test_roman.py`) para respetar la unicidad de archivos de SPEC.md §4; la validación de este ítem ejecuta comprobaciones funcionales y de contrato de excepciones sobre el módulo real.

**Dependencies:** Item 1

**Validation:**
- Éxito: `PYTHONPATH=src python -c "from roman import to_roman, from_roman, MIN_VALUE, MAX_VALUE, NUMERAL_TABLE, CANONICAL_RE, __all__; assert MIN_VALUE == 1 and MAX_VALUE == 3999; assert len(NUMERAL_TABLE) == 13; assert to_roman(1) == 'I'; assert to_roman(4) == 'IV'; assert to_roman(9) == 'IX'; assert to_roman(1994) == 'MCMXCIV'; assert to_roman(3999) == 'MMMCMXCIX'; assert from_roman('iv') == 4; assert from_roman('McmXCiv') == 1994; assert from_roman('mmmcmxcix') == 3999; assert __all__ == ['to_roman', 'from_roman', 'MIN_VALUE', 'MAX_VALUE']; print('OK core')"`
- Errores: `PYTHONPATH=src python -c "from roman import to_roman, from_roman;
for bad in (True, False, 1.0, '1', None, [1], 3+0j):
    try: to_roman(bad)
    except TypeError: pass
    else: raise SystemExit(f'TypeError esperado para {bad!r}')
for bad in (0, -1, -3999, 4000, 10**6):
    try: to_roman(bad)
    except ValueError: pass
    else: raise SystemExit(f'ValueError esperado para {bad!r}')
for bad in ('', 'IIII', 'VV', 'IC', 'MMMM', 'IV\n'):
    try: from_roman(bad)
    except ValueError: pass
    else: raise SystemExit(f'ValueError esperado para {bad!r}')
print('OK errores')"`
- Estándar only: `grep -q '^import re$' src/roman.py && ! grep -Eq 'os\.(environ|getenv)|import os|requests|pydantic' src/roman.py`

**Role:** role-dev (backend_developer)

### ITEM 3: Suite de pruebas pytest — `tests/test_roman.py` (valores conocidos, contratos de error y roundtrip 1..3999)

**Goal:** Implementar la suite completa en un único módulo pytest, con `import pytest` + `from roman import to_roman, from_roman, MIN_VALUE, MAX_VALUE`, funciones planas y `@pytest.mark.parametrize`. Solo se asertan **tipos** de excepción (nunca substrings de mensaje). Funciones requeridas:

- `test_to_roman_known_values` (parametrizado: 1→`I`, 2→`II`, 3→`III`, 4→`IV`, 5→`V`, 9→`IX`, 10→`X`, 14→`XIV`, 40→`XL`, 44→`XLIV`, 50→`L`, 90→`XC`, 99→`XCIX`, 100→`C`, 400→`CD`, 444→`CDXLIV`, 500→`D`, 900→`CM`, 944→`CMXLIV`, 1000→`M`, 1666→`MDCLXVI`, 1994→`MCMXCIV`, 2024→`MMXXIV`, 3999→`MMMCMXCIX`).
- `test_to_roman_lower_bound` (`to_roman(1) == "I"`), `test_to_roman_upper_bound` (`to_roman(3999) == "MMMCMXCIX"`), `test_to_roman_returns_str` (`isinstance(..., str)` en una muestra), `test_to_roman_subtractive_forms` (4→`IV`, 9→`IX`, 40→`XL`, 90→`XC`, 400→`CD`, 900→`CM`).
- `test_to_roman_rejects_bool` (`True`, `False` → `TypeError`), `test_to_roman_rejects_non_int` (`1.0`, `"1"`, `None`, `[1]`, `3+0j` → `TypeError`), `test_to_roman_rejects_below_range` (`0`, `-1`, `-3999` → `ValueError`), `test_to_roman_rejects_above_range` (`4000`, `4001`, `10**6` → `ValueError`).
- `test_from_roman_known_values` (inverso de la tabla anterior), `test_from_roman_accepts_lowercase` (`"iv"`→4, `"mmmcmxcix"`→3999, `"mcmxciv"`→1994), `test_from_roman_accepts_mixed_case` (`"McmXCiv"`→1994, `"iV"`→4), `test_from_roman_returns_int` (`isinstance(from_roman("X"), int)` y `not isinstance(..., bool)`).
- `test_from_roman_rejects_empty` (`""` → `ValueError`), `test_from_roman_rejects_non_canonical` (`"IIII"`, `"VV"`, `"IC"`, `"MMMM"` → `ValueError`), `test_from_roman_rejects_other_non_canonical` (`"IL"`, `"VX"`, `"XXXX"`, `"LC"`, `"DM"`, `"VIIII"`, `"CCCC"`, `"DD"`, `"XM"`, `"IIX"` → `ValueError`), `test_from_roman_rejects_invalid_characters` (`"ABC"`, `"IV "`, `" IV"`, `"IV\n"`, `"I I"`, `"Ⅳ"` → `ValueError`).
- `test_roundtrip_1_to_3999` (`from_roman(to_roman(n)) == n` para `n in range(1, 4000)`, parametrizado), `test_roundtrip_all_canonical_strings` (`to_roman(from_roman(s)) == s` para todo `s = to_roman(n)`, `n in 1..3999`), `test_constants` (`MIN_VALUE == 1`, `MAX_VALUE == 3999`, `len(NUMERAL_TABLE) == 13`).

**Files to create:**
- `tests/test_roman.py` (create) - suite pytest descrita arriba; solo `pytest` y `roman` como imports; sin `unittest`, sin mocks, sin servicios externos

**Tests required:**
- Este ítem **es** la entrega de pruebas: 20 funciones de test que cubren happy path, contratos de error y roundtrip bidireccional 1..3999.

**Dependencies:** Item 1, Item 2

**Validation:** `python -m pytest -q` desde la raíz finaliza con 0 fallos; comprobación de recuento/cobertura de casos: `python -m pytest -q --collect-only | tail -n 3` muestra las 20 funciones (con sus parametrizaciones) y `python -m pytest -q -k roundtrip` pasa en verde.

**Role:** role-dev (backend_developer)

### ITEM 4: Documentación breve (`README.md`) y puerta de calidad final

**Goal:** Redactar el `README.md` (40–70 líneas) y ejecutar la verificación integral del repositorio, con contenido exacto:

1. Descripción en una línea del conversor y su carácter de librería interna.
2. Requisito `Python >= 3.9` (interprete de referencia 3.11) y nota "solo librería estándar: sin dependencias de runtime, sin servidor, sin interfaz".
3. Instalación: `pip install -e .` y `pip install -e ".[test]"`.
4. Uso con ejemplos reales: `to_roman(1994) == "MCMXCIV"`, `to_roman(3999) == "MMMCMXCIX"`, `from_roman("mcmxciv") == 1994` (se acepta minúsculas/mixtas).
5. Tabla de API: `to_roman(n: int) -> str` y `from_roman(s: str) -> int`, con dominio 1..3999.
6. Tabla de excepciones: `TypeError` para no-`int` (incluido `bool`), `ValueError` fuera de rango, `ValueError` para cadena vacía y no canónica.
7. Reglas de canonicidad (forma sustractiva, máximo tres repeticiones, casos inválidos `IIII`, `VV`, `IC`, `MMMM`).
8. Comando de tests: `python -m pytest`.
9. Cierre con la verificación final: suite completa en verde y árbol de archivos limitado a los cuatro archivos de SPEC.md §4.

**Files to create:**
- `README.md` (create) - descripción, requisitos, instalación, uso, tabla API, tabla de excepciones, reglas de canonicidad, comando pytest y nota de alcance (sin dependencias/servidor/interfaz)

**Tests required:**
- No aplica (documentación). La validación ejecuta la suite completa del Item 3 como puerta de calidad y verifica la ausencia de archivos fuera de alcance.

**Dependencies:** Item 1, Item 2, Item 3

**Validation:** `python -m pytest -q` en verde; `python -c "import pathlib; t = pathlib.Path('README.md').read_text(encoding='utf-8'); assert all(k in t for k in ('pip install -e .', 'to_roman', 'from_roman', 'python -m pytest', 'TypeError', 'ValueError'))"`; alcance: `test ! -e Dockerfile && test ! -e docker-compose.yml && test ! -e run.sh && test ! -e .env.example && test ! -d frontend && test ! -d backend && test ! -d shared && find . -type f -not -path './.git/*' -not -path '*/__pycache__/*' -not -path './.pytest_cache/*' -not -path '*.egg-info/*' | sort` devuelve exactamente `README.md`, `pyproject.toml`, `src/roman.py`, `tests/test_roman.py`.

**Role:** role-dev (backend_developer)