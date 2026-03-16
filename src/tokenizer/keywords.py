from tokenizer.tokens import Token


class KEYWORD(Token):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __repr__(self) -> str:
        return str(self)


KEYWORDS: dict[str, type[KEYWORD]] = {}

def register_keyword(keyword_text):
    def wrapper(cls):
        KEYWORDS[keyword_text] = cls
        return cls
    return wrapper

class SEMICOLON(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return ";"

class OPEN_BRACKET(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "("

class CLOSE_BRACKET(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return ")"

class OPEN_C_BRACKET(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "{"

class CLOSE_C_BRACKET(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "}"

@register_keyword("exit")
class EXIT_KEYWORD(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "exit"

@register_keyword("while")
class WHILE_KEYWORD(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "while"

@register_keyword("for")
class FOR_KEYWORD(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "for"

@register_keyword("const")
class CONST_KEYWORD(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "const"

@register_keyword("int64")
class INT64_KEYWORD(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "int64"

@register_keyword("char")
class CHAR_KEYWORD(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "char"

@register_keyword("print")
class PRINT_KEYWORD(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "print"

@register_keyword("if")
class IF_KEYWORD(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "if"

@register_keyword("else")
class ELSE_KEYWORD(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "else"

class ASSIGN_KEYWORD(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

    def __str__(self) -> str:
        return "="

class MATH_OPERATION(KEYWORD):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

class PLUS_KEYWORD(MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 3

    def __str__(self) -> str:
        return "+"

class MINUS_KEYWORD(MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 3

    def __str__(self) -> str:
        return "-"

class MULTIPLY_KEYWORD(MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 4

    def __str__(self) -> str:
        return "*"

class INT_DIVISION_KEYWORD(MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 4

    def __str__(self) -> str:
        return "//"

class UNARY_MATH_OPERATION(MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

class INCREMENT_KEYWORD(UNARY_MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 5

    def __str__(self) -> str:
        return "++"

class DECREMENT_KEYWORD(UNARY_MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 5

    def __str__(self) -> str:
        return "--"

class MODULO_KEYWORD(MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 4

    def __str__(self) -> str:
        return "%"

class GREATER_KEYWORD(MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 2

    def __str__(self) -> str:
        return ">"

class LESS_KEYWORD(MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 2

    def __str__(self) -> str:
        return "<"

class GREATER_OR_EQUALS_KEYWORD(MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 2

    def __str__(self) -> str:
        return ">="

class LESS_OR_EQUALS_KEYWORD(MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 2

    def __str__(self) -> str:
        return "<="

class EQUALS_KEYWORD(MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 1

    def __str__(self) -> str:
        return "=="

class NOT_EQUALS_KEYWORD(MATH_OPERATION):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)
        self.bpower: int = 1

    def __str__(self) -> str:
        return "!="
