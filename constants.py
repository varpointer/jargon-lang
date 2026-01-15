from types_ import BasicType as _Type
LETTERS_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LETTERS_LOWER = "abcdefghijklmnopqrstuvwxyz"
LETTERS = LETTERS_UPPER + LETTERS_LOWER
NUMBERS = "0123456789"
ALPHANUMERIC = LETTERS + NUMBERS
KEYWORDS: dict[str, str] = {
    "declare_var": "var",
    "declare_func": "func",
    "return_value": "return",
    "condition_main": "if",
    "condition_alt": "elseif",
    "condition_fail": "else",
    "loop_condition": "while",
    "control_next": "continue",
    "control_end": "break",
    "loop_threepart": "for",
}
TYPES: dict[str, _Type] = {
    "int": _Type.INT,
    "float": _Type.FLOAT,
    "char": _Type.CHAR,
    "str": _Type.STR,
}

VERSION_MAJOR = 0
VERSION_MINOR = 21
VERSION_PATCH = 0

RELEASE_YEAR  = 2026
RELEASE_MONTH = 1
RELEASE_DAY   = 15
