from tokenizer.keywords import ASSIGN_KEYWORD, CLOSE_BRACKET, CLOSE_C_BRACKET, DECREMENT_KEYWORD, EQUALS_KEYWORD, GREATER_KEYWORD, GREATER_OR_EQUALS_KEYWORD, INCREMENT_KEYWORD, INT64_KEYWORD, INT_DIVISION_KEYWORD, KEYWORDS, LESS_KEYWORD, LESS_OR_EQUALS_KEYWORD, MINUS_KEYWORD, MODULO_KEYWORD, MULTIPLY_KEYWORD, NOT_EQUALS_KEYWORD, OPEN_BRACKET, OPEN_C_BRACKET, PLUS_KEYWORD, SEMICOLON
from tokenizer.literals import CHAR_LITERAL, INT_LITERAL
from tokenizer.tokens import Token, IDENTIFIER


class Tokenizer:
    def __init__(self, src_code: str) -> None:
        self._src: str = src_code
        self._src_len: int = len(src_code)
        self._line_num: int = 1
        self._idx: int = 0
        self._stop_chars: list[str] = [" ", "\n", "\t", ";", "(", ")", "{", "}", "=", "+", "-", "*", ">", "<", "%", "/", "!"]
        self._c_brackets: int = 0

    def _peek(self, offset: int = 0) -> str | None:
        return self._src[self._idx + offset] if self._idx + offset < self._src_len else None

    def _consume(self) -> str:
        self._idx += 1
        return self._src[self._idx - 1]

    def _assemble_int(self, first_char: str) -> int:
        number = first_char
        while self._peek() and self._peek() not in self._stop_chars:
            if self._peek().isalpha():
                raise ValueError(f"invalid syntax in line {self._line_num}")
            number_char = self._consume()
            if not number_char.isdigit():
                self._idx -= 1
                break
            number += number_char
        return int(number)

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []

        while self._peek():
            char: str = self._consume()

            if char.isalpha():
                word = char
                while self._peek() is not None and self._peek() not in self._stop_chars:
                    word += self._consume()

                if word in KEYWORDS:
                    tokens.append(KEYWORDS[word](self._line_num))
                else:
                    tokens.append(IDENTIFIER(self._line_num, word))

            elif char.isdigit():
                tokens.append(INT_LITERAL(self._line_num, self._assemble_int(char)))

            elif char in [" ", "\t"]:
                pass

            elif char == "'":
                if self._peek() == "\\":
                    self._consume()
                    match self._consume():
                        case "n":
                            char_value = "\n"
                        case "t":
                            char_value = "\t"
                        case "\\":
                            char_value = "\\"
                        case "0":
                            char_value = "\0"
                        case "'":
                            char_value = "'"
                        case _:
                            raise ValueError(f"invalid char in line {self._line_num}")
                else:
                    char_value = self._consume()

                if self._peek() != "'":
                    raise ValueError(f"syntax error in line {self._line_num} (expected closing quote for char)")

                self._consume()
                tokens.append(CHAR_LITERAL(self._line_num, ord(char_value)))

            elif char == "/":
                match self._peek():
                    case "/":
                        self._consume()
                        tokens.append(INT_DIVISION_KEYWORD(self._line_num))
                    case "*":
                        self._consume()
                        ln = self._line_num
                        while not (self._peek() == "*" and self._peek(1) == "/"):
                            if self._peek() is None:
                                raise ValueError(f"multiline comment was never closed (opened in line {ln})")
                            if self._consume() == "\n":
                                self._line_num += 1
                        self._consume()
                        self._consume()
                    case _:
                        raise ValueError(f"invalid syntax after '/' in line {self._line_num}")

            elif char == "%":
                tokens.append(MODULO_KEYWORD(self._line_num))

            elif char == "{":
                tokens.append(OPEN_C_BRACKET(self._line_num))
                self._c_brackets += 1

            elif char == "!":
                match self._peek():
                    case "=":
                        self._consume()
                        tokens.append(NOT_EQUALS_KEYWORD(self._line_num))
                    case _:
                        raise ValueError(f"invalid syntax after '!' in line {self._line_num}")
            
            elif char == "}":
                tokens.append(CLOSE_C_BRACKET(self._line_num))
                self._c_brackets -= 1
            
            elif char == "(":
                tokens.append(OPEN_BRACKET(self._line_num))
            
            elif char == ")":
                tokens.append(CLOSE_BRACKET(self._line_num))
            
            elif char == ">":
                if self._peek() == "=":
                    self._consume()
                    tokens.append(GREATER_OR_EQUALS_KEYWORD(self._line_num))
                else:
                    tokens.append(GREATER_KEYWORD(self._line_num))
            
            elif char == "<":
                if self._peek() == "=":
                    self._consume()
                    tokens.append(LESS_OR_EQUALS_KEYWORD(self._line_num))
                else:
                    tokens.append(LESS_KEYWORD(self._line_num))
            
            elif char == "=":
                match self._peek():
                    case "=":
                        self._consume()
                        tokens.append(EQUALS_KEYWORD(self._line_num))
                    case _:
                        tokens.append(ASSIGN_KEYWORD(self._line_num))
            
            elif char == "+":
                if self._peek() is not None and self._peek() == "+":
                    self._consume()
                    tokens.append(INCREMENT_KEYWORD(self._line_num))
                else:
                    tokens.append(PLUS_KEYWORD(self._line_num))
            
            elif char == "-":
                if self._peek() is not None and self._peek() == "-":
                    self._consume()
                    tokens.append(DECREMENT_KEYWORD(self._line_num))
                    continue

                tokens.append(MINUS_KEYWORD(self._line_num))

            elif char == "*":
                tokens.append(MULTIPLY_KEYWORD(self._line_num))
            
            elif char == ";":
                tokens.append(SEMICOLON(self._line_num))
            
            elif char == "\n":
                self._line_num += 1
            
            elif char == "#":
                while self._peek() is not None and self._consume() != "\n":
                    pass
                self._line_num += 1
            
            else:
                raise ValueError(f"unknown character '{char}' in line {self._line_num}")

        if self._c_brackets != 0:
            raise ValueError("unmatched number of opened and closed curly brackets")

        return tokens
