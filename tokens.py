from enum import Enum
from typing import Any
from pos import Position

TokenType = Enum("TokenType", [
    "EOF", "INT", "FLOAT", "PLUS", "MINUS", "ASTERISK", "SLASH", "L_PAREN", "R_PAREN",
    "STR", "CHAR", "GT", "GE", "LT", "LE", "EQEQ", "NOTEQ", "PIPE", "PIPEPIPE", "AND",
    "ANDAND", "CARET", "EXCLAMATION", "TILDE", "IDENTIFIER", "KEYWORD", "COLON", "EQUALS",
    "TYPE", "SEMICOLON", "L_BRACE", "R_BRACE", "COMMA", "ARROW", "L_BRACKET", "R_BRACKET"
])

class Token:
    def __init__(self, token_type: TokenType, value: Any, pos_start: Position, pos_end: Position):
        self.token_type = token_type
        self.value = value
        self.pos_start = pos_start
        self.pos_end = pos_end
    def __repr__(self):
        string_repr: str = f"[{self.token_type.name}"
        if self.value:
            string_repr += f":{self.value!r}"
        string_repr += "]"
        return string_repr
    def match(self, token_type: TokenType, value) -> bool:
        return self.token_type == token_type and value == self.value
    
    def match_keyword(self, keyword: str):
        return (self.token_type == TokenType.KEYWORD) and (self.value == keyword)            
