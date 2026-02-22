from tokenizer.keywords import KEYWORDS, SEMICOLON
from tokenizer.literals import INT_LITERAL
from tokenizer.tokens import Token, IDENTIFIER


class Tokenizer:
    def __init__(self, src_code: str) -> None:
        self._src: str = src_code
        self._src_len: int = len(src_code)
        self._line_num: int = 1
        self._idx: int = 0
        self._stop_chars: list[str] = [" ", "\n", "\t", ";"]

    def _peek(self, offset: int = 0) -> str | None:
        return self._src[self._idx + offset] if self._idx + offset < self._src_len else None

    def _consume(self) -> str:
        self._idx += 1
        return self._src[self._idx - 1]

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []

        while self._peek():
            char: str = self._consume()

            if char.isalpha():
                word = char
                while self._peek() and self._peek() not in self._stop_chars:
                    word += self._consume()

                if word in KEYWORDS:
                    tokens.append(KEYWORDS[word](self._line_num))
                else:
                    tokens.append(IDENTIFIER(self._line_num, word))

            elif char.isdigit():
                number = char
                while self._peek() and self._peek() not in self._stop_chars:
                    number_char = self._consume()
                    if not number_char.isdigit():
                        raise ValueError(f"invalid digit '{number_char}' in line {self._line_num}")
                    number += number_char
                tokens.append(INT_LITERAL(self._line_num, int(number)))
            
            elif char in [" ", "\t"]:
                pass

            elif char == ";":
                tokens.append(SEMICOLON(self._line_num))
            
            elif char == "\n":
                self._line_num += 1
            
            else:
                raise ValueError(f"unknown character '{char}' in line {self._line_num}")

        return tokens
