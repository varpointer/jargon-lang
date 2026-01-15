from tokens import Token, TokenType
from result import LexerResult as Result
from pos import Position
from copy import copy
from error import Error
from constants import LETTERS, KEYWORDS, TYPES, NUMBERS, ALPHANUMERIC

class Lexer:
    token_table = {
        "\x1a": TokenType.EOF,
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.ASTERISK,
        "(": TokenType.L_PAREN,
        ")": TokenType.R_PAREN,
        "=": TokenType.EQUALS,
        "==": TokenType.EQEQ,
        "^": TokenType.CARET,
        "&": TokenType.AND,
        "&&": TokenType.ANDAND,
        "|": TokenType.PIPE,
        "||": TokenType.PIPEPIPE,
        "!": TokenType.EXCLAMATION,
        "~": TokenType.TILDE,
        ">": TokenType.GT,
        ">=": TokenType.GE,
        "<": TokenType.LT,
        "<=": TokenType.LE,
        ":": TokenType.COLON,
        ";": TokenType.SEMICOLON,
        "{": TokenType.L_BRACE,
        "}": TokenType.R_BRACE,
        ",": TokenType.COMMA,
        "->": TokenType.ARROW,
        "[": TokenType.L_BRACKET,
        "]": TokenType.R_BRACKET,
    }
    def __init__(self, text: str):
        self.text = text
        self.current_char: str = "\0"
        self.pos = Position(-1, 0, -1)
        self.tokens: list[Token] = []
        self.advance()

    def advance(self):
        "Advances to the next character then returns it. Returns EOF if there are no characters left"
        self.pos.increment()
        if self.pos.index >= len(self.text):
            self.current_char = "\x1a" 
        else:
            if self.current_char == "\n":
                self.pos.newline()
            self.current_char = self.text[self.pos.index]
        return self.current_char
        
    def lex_text(self) -> tuple[list[Token], Error | None]:
        while True:
            gen_result = self.gen_token()
            if not gen_result.is_success():
                return ([], gen_result.err)
            if not gen_result.ok:
                continue
            token = gen_result.get_success()
            self.tokens.append(token)
            if token.token_type == TokenType.EOF: 
                break
        return (self.tokens, None) 
    
    def gen_token(self) -> Result:
        "Generates a token from the current character and advances as necessary."
        current_char = self.current_char
        pos_start = copy(self.pos)
        if self.current_char in self.token_table:
            char = self.current_char
            token_type = self.token_table[char]
            self.advance()
            if char + self.current_char in self.token_table:
                token_type = self.token_table[char + self.current_char]
                self.advance()
            return Result(Token(token_type, None, pos_start, copy(self.pos)))
        elif self.current_char in NUMBERS + ".":
            return self.gen_number()
        elif self.current_char in " \n\t":
            self.advance()
            return Result(None)
        elif self.current_char == "/":
            self.advance()
            if self.current_char == "/":
                self.comment()
                return Result(None)
            elif self.current_char == "*":
                self.multiline_comment()
                return Result(None)
            return Result(Token(TokenType.SLASH, None, pos_start, copy(self.pos)))
        elif self.current_char == '"':
            return self.gen_string()
        elif self.current_char == "'":
            self.advance()
            char = self.current_char
            self.advance()
            if self.current_char != "'":
                return Result(None, Error(f"Expected \"'\"", pos_start, self.pos+1))
            self.advance()
            return Result(Token(TokenType.CHAR, char, pos_start, copy(self.pos)))
        elif self.current_char in LETTERS + "_":
            return self.gen_ident()
        return Result(None, Error(f"Unexpected character: {current_char!r}", pos_start, self.pos+1))
    
    def gen_number(self) -> Result:
        num_str = ""
        pos_start = copy(self.pos)
        token_type: TokenType = TokenType.INT
        contains_decimal_point = False
        while self.current_char in "0123456789.":
            if self.current_char == ".":
                if contains_decimal_point:
                    break
                contains_decimal_point = True
                token_type = TokenType.FLOAT
            num_str += self.current_char
            self.advance()
        if num_str == ".":
            num_str = "0.0"
        return Result(Token(token_type, num_str, pos_start, copy(self.pos)))
    
    def gen_string(self) -> Result:
        string = ""
        pos_start = copy(self.pos)
        escape = False
        while True:
            self.advance()
            if self.current_char == '"' and not escape:
                break
            if self.current_char == "\\" and not escape:
                escape = True
            else:
                escape = False
            if self.current_char == "\x1a":
                return Result(None, Error("Unterminated string literal, expected '\"'", pos_start, copy(self.pos)))
            string += self.current_char
        pos_end = copy(self.pos)
        self.advance()
        return Result(Token(TokenType.STR, string, pos_start, pos_end))

    def gen_ident(self) -> Result:
        pos_start = copy(self.pos)
        text = ""
        while self.current_char in ALPHANUMERIC  +"_":
            text += self.current_char
            self.advance()
        
        return Result(Token((
            TokenType.KEYWORD if text in KEYWORDS.values() else
            TokenType.TYPE if text in TYPES.keys() else
            TokenType.IDENTIFIER
        ), text, pos_start, copy(self.pos)))

    def comment(self):
        while self.current_char not in "\n\x1a":
            self.advance()
    def multiline_comment(self):
        while True:
            if self.current_char == "*" and self.advance() == "/" or self.current_char == "\x1b":
                break
            self.advance()
        self.advance()
