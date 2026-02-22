from tokenizer.tokens import Token


class KEYWORD(Token):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

class SEMICOLON(KEYWORD):
    _keyword_text: str = ";"
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "SEMICOLON"

    def __repr__(self) -> str:
        return str(self)

class EXIT_KEYWORD(KEYWORD):
    _keyword_text: str = "exit"
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "EXIT_KEYWORD"

    def __repr__(self) -> str:
        return str(self)

KEYWORDS: dict[str, type[KEYWORD]] = {}
for cls in KEYWORD.__subclasses__():
    KEYWORDS[cls._keyword_text] = cls
