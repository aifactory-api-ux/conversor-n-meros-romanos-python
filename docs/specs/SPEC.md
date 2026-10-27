# SPEC.md

## Project: `roman` — Minimal Roman Numeral Conversion Library

**Scope statement (authoritative):** This project is a *small Python library* consisting of one source module (`src/roman.py`), one pytest test module (`tests/test_roman.py`), and a brief `README.md`. The library exposes exactly two public functions, `to_roman` and `from_roman`, used by the internal engineering team as a dependency inside other Python scripts.

**Explicit exclusions (from the goal):** *"Solo librería estándar, sin servidor ni interfaz."* → no web server, no HTTP endpoints, no CLI, no frontend, no database, no container, no cloud infrastructure, no third-party runtime dependencies, no network calls, no environment configuration, no observability stack.

---

## 1. TECHNOLOGY STACK

| Item | Exact choice | Notes |
|---|---|---|
| Language | Python | `from __future__ import annotations` is NOT used; builtin generics require 3.9+ |
| Minimum Python version | 3.9 | `tuple[tuple[int, str], ...]` style annotations require ≥3.9 |
| Target Python version | 3.11 | Reference interpreter for test runs |
| Runtime dependencies | **None** — standard library only | Explicit requirement: *"Solo librería estándar"* |
| Standard library modules used | `re` (only) | Used for canonical-form validation |
| Test framework | `pytest` >= 7.0 | **Test-only** dependency; never imported by `src/roman.py` |
| Test configuration | `[tool.pytest.ini_options]` in `pyproject.toml` with `pythonpath = ["src"]` | Makes `import roman` resolve to `src/roman.py` without installation |
| Build/packaging metadata | `pyproject.toml` (PEP 621), build backend `setuptools.build_meta` | Required to satisfy *"La usará el equipo de ingeniería interno como dependencia en otros scripts Py"* — the module must be installable/importable as a package |
| Packaging name | `roman-numerals-lib` (distribution), import name `roman` | Import name MUST be `roman` because tests and consumers do `from roman import to_roman, from_roman` |
| Type checking | Type hints in signatures only; no `mypy` configuration required | Not requested |
| Linters/formatters | None configured | Not requested — do not add |
| Containerization | **None** | Explicitly out of scope (`sin servidor`) |
| CI | **None** | Not requested |

---

## 2. DATA CONTRACTS

This is a Python library with no persistence and no Pydantic models (Pydantic is a third-party dependency and is therefore forbidden). The data contracts are: (a) the exact public function signatures, (b) the module-level constants that define the numeral domain, and (c) the exact exception contract per input class.

### 2.1 Module-level constants — `src/roman.py`

These names are part of the import contract and MUST appear verbatim:

```python
from __future__ import annotations  # NOT used — omit

import re

MIN_VALUE: int = 1
MAX_VALUE: int = 3999

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

CANONICAL_PATTERN: str = r"M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})"
CANONICAL_RE: re.Pattern[str] = re.compile(CANONICAL_PATTERN)

__all__: list[str] = ["to_roman", "from_roman", "MIN_VALUE", "MAX_VALUE"]
```

**Contract rules for the constants:**

* `NUMERAL_TABLE` is ordered **descending** by value and MUST contain exactly the 13 pairs above. The subtractive pairs (`CM`, `CD`, `XC`, `XL`, `IX`, `IV`) are the *only* representation of the subtractive form.
* `CANONICAL_PATTERN` has **no `^` anchor and no `$` anchor**. Validation MUST use `CANONICAL_RE.fullmatch(text)` so that a trailing newline (`"IV\n"`) is rejected. (`$` would wrongly accept `"IV\n"`.)
* `MIN_VALUE` / `MAX_VALUE` bound the domain for both directions.

### 2.2 Public function signatures

```python
def to_roman(n: int) -> str:
    """Convert an integer in 1..3999 to its canonical subtractive roman numeral.

    Raises:
        TypeError: if ``n`` is not an ``int`` (``bool`` explicitly included,
            because ``bool`` is a subclass of ``int``).
        ValueError: if ``n`` is outside ``MIN_VALUE..MAX_VALUE`` (1..3999).
    """


def from_roman(s: str) -> int:
    """Convert a canonical roman numeral string to an integer in 1..3999.

    Accepts lower case, upper case, and mixed case input.

    Raises:
        ValueError: if ``s`` is empty, or if ``s`` is not a canonical roman
            numeral (e.g. ``"IIII"``, ``"VV"``, ``"IC"``, ``"MMMM"``).
    """
```

### 2.3 Type contract table

| Function | Parameter | Declared type | Accepted runtime values | Return type | Return range |
|---|---|---|---|---|---|
| `to_roman` | `n` | `int` | `int` only; `bool` rejected | `str` | Canonical numeral for 1..3999 |
| `from_roman` | `s` | `str` | `str` only (any case) | `int` | 1..3999 |

**Undefined behaviour (explicitly NOT part of the contract, must not be tested):** `from_roman` with a non-`str` argument (`None`, `4`, `b"IV"`). The declared type is `str`; the implementation may assume `str`. No `TypeError` contract exists for `from_roman`.

### 2.4 Exception contract table (authoritative)

| Function | Input | Exception | Message constant (exact text) |
|---|---|---|---|
| `to_roman` | `True`, `False` | `TypeError` | `"to_roman() expects int, got bool"` |
| `to_roman` | `1.0`, `"1"`, `None`, `[1]`, `3 + 0j` | `TypeError` | `"to_roman() expects int, got <typename>"` |
| `to_roman` | `0`, `-1`, `-3999`, `4000`, `10**6` | `ValueError` | `"to_roman() argument must be in 1..3999, got <n>"` |
| `to_roman` | `1` … `3999` | — (returns `str`) | — |
| `from_roman` | `""` | `ValueError` | `"from_roman() argument must not be empty"` |
| `from_roman` | `"IIII"`, `"VV"`, `"IC"`, `"MMMM"`, any non-canonical string | `ValueError` | `"from_roman() argument is not a canonical roman numeral: <repr>"` |
| `from_roman` | valid canonical string, any case | — (returns `int`) | — |

Message constants are specified for code consistency; **tests MUST assert exception types only**, never message substrings.

### 2.5 Canonical numeral reference table (both directions must agree)

| Value | Numeral | Value | Numeral | Value | Numeral |
|---|---|---|---|---|---|
| 1 | `I` | 40 | `XL` | 400 | `CD` |
| 4 | `IV` | 50 | `L` | 500 | `D` |
| 5 | `V` | 90 | `XC` | 900 | `CM` |
| 9 | `IX` | 100 | `C` | 1000 | `M` |
| 10 | `X` | 3999 | `MMMCMXCIX` | 1994 | `MCMXCIV` |

### 2.6 Algorithms (must be implemented exactly)

**`to_roman`:**

1. Guard types: `if isinstance(n, bool) or not isinstance(n, int): raise TypeError(...)`. The `isinstance(n, bool)` check MUST come first because `bool` subclasses `int`.
2. Guard range: `if not MIN_VALUE <= n <= MAX_VALUE: raise ValueError(...)`.
3. Greedy subtraction: iterate `NUMERAL_TABLE` in order; `count, remainder = divmod(remainder, value)`; append `numeral * count` when `count > 0`.
4. Return `"".join(parts)`.

**`from_roman`:**

1. `if not s: raise ValueError(empty)` — empty string check comes first.
2. `upper = s.upper()` — this is how lower-case acceptance is implemented; no case-folding locale tricks, no trimming.
3. `if CANONICAL_RE.fullmatch(upper) is None: raise ValueError(non_canonical)`.
4. Left-to-right parse: for each `(value, numeral)` in `NUMERAL_TABLE`, consume repeated `numeral` prefixes from the cursor position and add `value` per consumption.
5. **Re-encode verification:** compute `result`; then `if to_roman(result) != upper: raise ValueError(non_canonical)`. This second gate guarantees `"IIII"`, `"VV"`, `"IC"`, `"MMMM"` and any other non-canonical string can never be accepted, even if the regex were relaxed later.
6. Return `result`.

---

## 3. API ENDPOINTS

**None.** The goal states explicitly: *"Solo librería estándar, sin servidor ni interfaz."* There is no HTTP server, no FastAPI/Flask app, no route table, no webhook, no `/metrics` endpoint, no admin endpoint, no export endpoint. No `main.py`, no `app.py`, no `uvicorn`, no port binding exists in this project.

The complete public *in-process* API surface (the only "API" this project has) is:

| Surface | Signature | Raises | File |
|---|---|---|---|
| `roman.to_roman` | `to_roman(n: int) -> str` | `TypeError`, `ValueError` | `src/roman.py` |
| `roman.from_roman` | `from_roman(s: str) -> int` | `ValueError` | `src/roman.py` |
| `roman.MIN_VALUE` | `int = 1` | — | `src/roman.py` |
| `roman.MAX_VALUE` | `int = 3999` | — | `src/roman.py` |

---

## 4. FILE STRUCTURE

```
/
├── README.md                  # Brief README: description, install, usage, API table, validation rules, pytest command
├── pyproject.toml             # PEP 621 metadata (name=roman-numerals-lib, import name=roman) + [tool.pytest.ini_options] pythonpath=["src"]
├── src/
│   └── roman.py               # The entire library: MIN_VALUE, MAX_VALUE, NUMERAL_TABLE, CANONICAL_PATTERN, CANONICAL_RE, to_roman, from_roman
└── tests/
    └── test_roman.py          # pytest suite: to_roman, from_roman, error contracts, roundtrip 1..3999
```

**No other files.** Specifically absent by explicit scope: `Dockerfile`, `docker-compose.yml`, `run.sh`, `start.sh`, `.env.example`, `infrastructure/`, `frontend/`, `backend/`, `requirements.txt`, any database migration, any monitoring config.

The single non-`.py` source-adjacent file `pyproject.toml` is present because the goal states the library *"La usará el equipo de ingeniería interno como dependencia en otros scripts Py"* — it makes `src/roman.py` installable (`pip install -e .`) and configures pytest's `pythonpath` so `import roman` resolves without installation.

### 4.1 PORT TABLE

**Not applicable.** This project contains zero backend services, zero frontends, and zero infrastructure containers. No port is allocated, exposed, or documented. No `EXPOSE`/`CMD` directives exist anywhere in the tree.

### 4.2 SHARED MODULES

**Not applicable.** There is exactly one source module (`src/roman.py`) and exactly one consumer module (`tests/test_roman.py`). No shared directory, no cross-service imports, no Dockerfile `COPY` requirements.

### 4.3 `pyproject.toml` required contents

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "roman-numerals-lib"
version = "1.0.0"
description = "Minimal roman numeral conversion library (to_roman / from_roman), standard library only."
requires-python = ">=3.9"
dependencies = []

[project.optional-dependencies]
test = ["pytest>=7.0"]

[tool.setuptools]
package-dir = { "" = "src" }

[tool.setuptools.py-modules]
roman = "roman"

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

---

## 5. ENVIRONMENT VARIABLES

**None.** The library reads **zero** environment variables, opens no files, makes no network calls, and has no configuration surface. There is no `.env`, no `.env.example`, no secrets file, no settings object. This follows directly from *"Solo librería estándar, sin servidor ni interfaz"* — a pure conversion library has no runtime configuration.

| Variable | Type | Description | Example |
|---|---|---|---|
| *(none)* | — | No environment variable is read or required by any file in this project. | — |

Verification rule for the generator: `src/roman.py` MUST NOT contain `os.environ`, `os.getenv`, `dotenv`, or any `import os` used for configuration.

---

## 6. IMPORT CONTRACTS

### `src/roman.py` — exports

```python
from roman import to_roman          # (n: int) -> str
from roman import from_roman        # (s: str) -> int
from roman import MIN_VALUE         # int = 1
from roman import MAX_VALUE         # int = 3999
from roman import NUMERAL_TABLE     # tuple[tuple[int, str], ...] — 13 descending pairs
from roman import CANONICAL_PATTERN # str regex source
from roman import CANONICAL_RE      # re.Pattern[str] (compiled, unanchored, use .fullmatch)
from roman import __all__           # ["to_roman", "from_roman", "MIN_VALUE", "MAX_VALUE"]
```

### `tests/test_roman.py` — imports

```python
import pytest
from roman import to_roman, from_roman, MIN_VALUE, MAX_VALUE
```

No relative imports (`from ..src.roman import ...`) are allowed anywhere; import resolution is provided solely by `pythonpath = ["src"]`.

### Internal imports inside `src/roman.py`

```python
import re
```

That is the only import permitted in `src/roman.py`. `pytest` MUST NOT be imported there.

---

## 7. FRONTEND STATE & COMPONENT CONTRACTS

**Not applicable — the project has no frontend.** The goal states *"sin servidor ni interfaz"* (no server, no interface). There are no React hooks, Vue composables, Angular services, Svelte stores, components, props, or UI state. No `.jsx`, `.tsx`, `.vue`, `.svelte`, `.html`, or `.css` file may be generated.

---

## 8. FILE EXTENSION CONVENTION

* **Language:** Python (100% of files). This is *not* a JavaScript/TypeScript project.
* **Source extensions:** `.py` for all code; `.md` for documentation; `.toml` for packaging/pytest configuration. Nothing else.
* **Frontend:** none — no `.jsx`, no `.tsx`, no `index.html`, no bundler entry point. There is no `<script src>` anywhere.
* **Library entry point (import path):** `src/roman.py`, importable as `roman` (e.g. `from roman import to_roman`).
* **Test entry point:** `tests/test_roman.py`, executed via `pytest` from the repository root.

---

## 9. DESIGN TOKENS

**Not applicable — no UI/UX Design Implementation Contract exists and the project has no user interface** (*"sin servidor ni interfaz"*). No `frontend/src/styles/tokens.ts`, no colour tokens, no typography tokens, no spacing scale may be generated.

---

## 10. FUNCTIONAL REQUIREMENTS COVERAGE

Every row below traces to a literal phrase in the goal statement. No requirement from the goal is omitted, and nothing outside the goal is added.

| # | Requirement (source phrase) | Implementation | Files |
|---|---|---|---|
| R1 | Library is "pequeña" and lives at exactly `src/roman.py` | Single module, ~60 lines, no sub-packages, no `__init__.py` in `src/` | `src/roman.py` |
| R2 | Expose `to_roman(n: int) -> str` with that exact name and signature | Public function `to_roman(n: int) -> str`; listed in `__all__` | `src/roman.py` |
| R3 | `to_roman` returns `str` | Returns `"".join(parts)`; never returns bytes or int | `src/roman.py` |
| R4 | Domain is 1..3999 | `MIN_VALUE = 1`, `MAX_VALUE = 3999`; range guard before conversion | `src/roman.py` |
| R5 | Lower bound 1 works | `to_roman(1) == "I"` (greedy table ends at `(1, "I")`) | `src/roman.py`, `tests/test_roman.py` |
| R6 | Upper bound 3999 works | `to_roman(3999) == "MMMCMXCIX"` | `src/roman.py`, `tests/test_roman.py` |
| R7 | "forma sustractiva" (subtractive notation) | `NUMERAL_TABLE` encodes `CM, CD, XC, XL, IX, IV` as single subtractive tokens; greedy `divmod` produces `IV` for 4, `IX` for 9, `XL` 40, `XC` 90, `CD` 400, `CM` 900 | `src/roman.py`, `tests/test_roman.py` |
| R8 | Subtractive results are exact (e.g. 4 → `IV`, not `IIII`) | Table-driven conversion guarantees no four-fold repeats; asserted by parametrized known-value test | `src/roman.py`, `tests/test_roman.py` |
| R9 | `ValueError` outside range | `if not MIN_VALUE <= n <= MAX_VALUE: raise ValueError(...)`; tested with `0`, `-1`, `-3999`, `4000`, `10**6` | `src/roman.py`, `tests/test_roman.py` |
| R10 | `TypeError` "si no es int" | `if not isinstance(n, int): raise TypeError(...)`; tested with `1.0`, `"1"`, `None`, `[1]`, `3+0j` | `src/roman.py`, `tests/test_roman.py` |
| R11 | "incluido bool" — `bool` must raise `TypeError` even though it subclasses `int` | Bool check ordered **first**: `if isinstance(n, bool) or not isinstance(n, int): raise TypeError(...)`; tested with `True` and `False` | `src/roman.py`, `tests/test_roman.py` |
| R12 | Expose `from_roman(s: str) -> int` with that exact name and signature | Public function `from_roman(s: str) -> int`; listed in `__all__` | `src/roman.py` |
| R13 | `from_roman` returns `int` | Returns parsed `int` from the greedy table walk; asserted with `isinstance(result, int)` | `src/roman.py`, `tests/test_roman.py` |
| R14 | "acepta minúsculas" (accepts lower case) | `upper = s.upper()` normalisation before validation; tested with `"iv"` → 4, `"mmmcmxcix"` → 3999, plus mixed case `"McmXCiv"` → 1994 | `src/roman.py`, `tests/test_roman.py` |
| R15 | `ValueError` for empty string | `if not s: raise ValueError(...)` executed before regex; tested with `""` | `src/roman.py`, `tests/test_roman.py` |
| R16 | `ValueError` for non-canonical `"IIII"` | Regex `I{0,3}` cap + re-encode gate `to_roman(result) != upper`; parametrized test case | `src/roman.py`, `tests/test_roman.py` |
| R17 | `ValueError` for non-canonical `"VV"` | Regex `V?I{0,3}` permits at most one `V` + re-encode gate; parametrized test case | `src/roman.py`, `tests/test_roman.py` |
| R18 | `ValueError` for non-canonical `"IC"` | Regex requires descending magnitude groups, `I` cannot precede `C`; fullmatch fails; parametrized test case | `src/roman.py`, `tests/test_roman.py` |
| R19 | `ValueError` for non-canonical `"MMMM"` | Regex `M{0,3}` caps `M` at three; parametrized test case | `src/roman.py`, `tests/test_roman.py` |
| R20 | General rejection of *any* non-canonical string (the four examples are illustrative) | Two independent gates: `CANONICAL_RE.fullmatch(upper)` and `to_roman(result) == upper`; extended parametrized cases `"IL"`, `"VX"`, `"XXXX"`, `"LC"`, `"DM"`, `"VIIII"`, `"CCCC"`, `"DD"`, `"XM"`, `"IIX"`, `"ABC"`, `"IV "`, `" IV"`, `"IV\n"`, `"I I"` | `src/roman.py`, `tests/test_roman.py` |
| R21 | Tests use pytest in exactly `tests/test_roman.py` | Single test module, plain `pytest` functions + `@pytest.mark.parametrize`, no `unittest.TestCase`, no other test file | `tests/test_roman.py` |
| R22 | Tests include roundtrip for 1..3999 | `test_roundtrip_1_to_3999` parametrized over `range(1, 4000)`: asserts `from_roman(to_roman(n)) == n`; companion `test_roundtrip_all_canonical_strings` asserts `to_roman(from_roman(s)) == s` for every canonical numeral | `tests/test_roman.py` |
| R23 | Roundtrip must also cover the *string→int→string* direction | Loop over `n in range(1, 4000)`, build `s = to_roman(n)`, assert `to_roman(from_roman(s)) == s` | `tests/test_roman.py` |
| R24 | `to_roman` known-value coverage | Parametrized cases: 1→`I`, 2→`II`, 3→`III`, 4→`IV`, 5→`V`, 9→`IX`, 10→`X`, 14→`XIV`, 40→`XL`, 44→`XLIV`, 50→`L`, 90→`XC`, 99→`XCIX`, 100→`C`, 400→`CD`, 444→`CDXLIV`, 500→`D`, 900→`CM`, 944→`CMXLIV`, 1000→`M`, 1666→`MDCLXVI`, 1994→`MCMXCIV`, 2024→`MMXXIV`, 3999→`MMMCMXCIX` | `tests/test_roman.py` |
| R25 | `from_roman` known-value coverage (inverse of R24) | Parametrized cases asserting each numeral above maps back to its integer | `tests/test_roman.py` |
| R26 | "README breve" (brief README) | `README.md` with: one-line description, Python ≥3.9 requirement, install (`pip install -e .`), usage snippets for both functions, API table, validation/exceptions table, canonical rules, `pytest` command, and a "no dependencies / no server / no UI" note. Target 40–70 lines. | `README.md` |
| R27 | "Solo librería estándar" — standard library only | `src/roman.py` imports only `re`; `dependencies = []` in `pyproject.toml`; pytest confined to `[project.optional-dependencies].test` and imported only by the test module | `src/roman.py`, `pyproject.toml`, `tests/test_roman.py` |
| R28 | "sin servidor" — no server | No web framework, no `app`, no routes, no `if __name__ == "__main__"` block, no socket/port, no ASGI/WSGI entry point, no Dockerfile | whole tree (absence) |
| R29 | "sin interfaz" — no interface | No CLI (`argparse`, `click`, `sys.argv` parsing), no TUI, no HTML/CSS/JS, no frontend directory | whole tree (absence) |
| R30 | "La usará el equipo de ingeniería interno como dependencia en otros scripts Py" — consumable as a dependency | Module importable as `roman` via `pyproject.toml` (`[tool.setuptools.py-modules] roman = "roman"`, `package-dir = {"" = "src"}`), so consumers write `from roman import to_roman, from_roman` | `pyproject.toml`, `src/roman.py`, `README.md` |
| R31 | Type hints required on both public functions | `to_roman(n: int) -> str` and `from_roman(s: str) -> int` annotated exactly as written in the goal | `src/roman.py` |
| R32 | Purity / determinism (implied by "librería" used as a dependency) | Both functions are pure: no global mutable state, no caching, no I/O, no randomness; `NUMERAL_TABLE` and `CANONICAL_RE` are module-level immutables/tuples | `src/roman.py` |

### 10.1 Test inventory (exact function names for `tests/test_roman.py`)

| Test function | Asserts |
|---|---|
| `test_to_roman_known_values` | R24 table (parametrized) |
| `test_to_roman_lower_bound` | `to_roman(1) == "I"` |
| `test_to_roman_upper_bound` | `to_roman(3999) == "MMMCMXCIX"` |
| `test_to_roman_returns_str` | `isinstance(to_roman(n), str)` for a sample of `n` |
| `test_to_roman_subtractive_forms` | 4→`IV`, 9→`IX`, 40→`XL`, 90→`XC`, 400→`CD`, 900→`CM` |
| `test_to_roman_rejects_bool` | `to_roman(True)` and `to_roman(False)` raise `TypeError` |
| `test_to_roman_rejects_non_int` | `1.0`, `"1"`, `None`, `[1]`, `3+0j` raise `TypeError` |
| `test_to_roman_rejects_below_range` | `0`, `-1`, `-3999` raise `ValueError` |
| `test_to_roman_rejects_above_range` | `4000`, `4001`, `10**6` raise `ValueError` |
| `test_from_roman_known_values` | R25 table (parametrized) |
| `test_from_roman_accepts_lowercase` | `"iv"`→4, `"mmmcmxcix"`→3999, `"mcmxciv"`→1994 |
| `test_from_roman_accepts_mixed_case` | `"McmXCiv"`→1994, `"iV"`→4 |
| `test_from_roman_returns_int` | `isinstance(from_roman("X"), int)` and not `bool` |
| `test_from_roman_rejects_empty` | `""` raises `ValueError` |
| `test_from_roman_rejects_non_canonical` | `"IIII"`, `"VV"`, `"IC"`, `"MMMM"` raise `ValueError` |
| `test_from_roman_rejects_other_non_canonical` | `"IL"`, `"VX"`, `"XXXX"`, `"LC"`, `"DM"`, `"VIIII"`, `"CCCC"`, `"DD"`, `"XM"`, `"IIX"` raise `ValueError` |
| `test_from_roman_rejects_invalid_characters` | `"ABC"`, `"IV "`, `" IV"`, `"IV\n"`, `"I I"`, `"Ⅳ"` raise `ValueError` |
| `test_roundtrip_1_to_3999` | `from_roman(to_roman(n)) == n` for `n in range(1, 4000)` (parametrized) |
| `test_roundtrip_all_canonical_strings` | `to_roman(from_roman(s)) == s` for all `s` produced by `to_roman(n)`, `n in 1..3999` |
| `test_constants` | `MIN_VALUE == 1`, `MAX_VALUE == 3999`, `len(NUMERAL_TABLE) == 13` |

### 10.2 Explicit non-requirements (must NOT be generated)

| Not required | Reason |
|---|---|
| HTTP server / FastAPI / Flask / endpoints | *"sin servidor"* |
| CLI entry point / `argparse` | Not requested; would violate *"sin interfaz"* |
| Frontend (React/Vue/HTML/CSS) | *"sin interfaz"* |
| Database, ORM, cache, queue | No persistence requirement exists |
| Docker / docker-compose / `run.sh` | Deployment not requested |
| `.env` / `.env.example` / secrets | Zero configuration surface (§5) |
| Prometheus / Grafana / tracing / `trace_id` | Observability not requested |
| PDF/CSV/HTML export | Not requested |
| Third-party runtime dependency | *"Solo librería estándar"* |
| `mypy`, `ruff`, `black`, `tox`, CI workflows | Not requested |
| Mocks, stubs, or placeholder implementations | Forbidden by the spec-writing contract; the real algorithms in §2.6 are the implementation |