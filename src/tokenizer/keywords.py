from tokenizer.tokens import Token


class KEYWORD(Token):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)


KEYWORDS: dict[str, type[KEYWORD]] = {}

def register_keyword(keyword_text):
    def wrapper(cls):
        KEYWORDS[keyword_text] = cls
        return cls
    return wrapper

@register_keyword(";")
class SEMICOLON(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "SEMICOLON"

    def __repr__(self) -> str:
        return str(self)

@register_keyword("exit")
class EXIT_KEYWORD(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "EXIT_KEYWORD"

    def __repr__(self) -> str:
        return str(self)

