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
        return ";"

    def __repr__(self) -> str:
        return str(self)

@register_keyword("exit")
class EXIT_KEYWORD(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "exit"

    def __repr__(self) -> str:
        return str(self)

@register_keyword("let")
class LET_KEYWORD(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "let"

    def __repr__(self) -> str:
        return str(self)

@register_keyword("print")
class PRINT_KEYWORD(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "print"

    def __repr__(self) -> str:
        return str(self)

@register_keyword("=")
class ASSIGN_KEYWORD(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "="

    def __repr__(self) -> str:
        return str(self)

class MATH_OPERATION(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

@register_keyword("+")
class PLUS_KEYWORD(MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 1

    def __str__(self) -> str:
        return "+"

    def __repr__(self) -> str:
        return str(self)

@register_keyword("-")
class MINUS_KEYWORD(MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 1

    def __str__(self) -> str:
        return "-"

    def __repr__(self) -> str:
        return str(self)

@register_keyword("*")
class MULTIPLY_KEYWORD(MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 2

    def __str__(self) -> str:
        return "*"

    def __repr__(self) -> str:
        return str(self)

@register_keyword("//")
class INT_DIVISION_KEYWORD(MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 2

    def __str__(self) -> str:
        return "//"

    def __repr__(self) -> str:
        return str(self)

@register_keyword("%")
class MODULO_KEYWORD(MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 2

    def __str__(self) -> str:
        return "%"

    def __repr__(self) -> str:
        return str(self)
