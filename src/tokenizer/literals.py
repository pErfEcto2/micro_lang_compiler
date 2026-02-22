from tokenizer.tokens import Token


class LITERAL(Token):
    def __init__(self, line_num: int) -> None:
        super().__init__(line_num)

class INT_LITERAL(LITERAL):
    def __init__(self, line_num: int, val: int) -> None:
        super().__init__(line_num)
        self.val: int = val

    def __str__(self) -> str:
        return f"INT_LITERAL({self.val})"

    def __repr__(self) -> str:
        return str(self)

class STR_LITERAL(LITERAL):
    def __init__(self, line_num: int, val: str) -> None:
        super().__init__(line_num)
        self.val: str = val

    def __str__(self) -> str:
        return f"STR_LITERAL({self.val})"

    def __repr__(self) -> str:
        return str(self)

