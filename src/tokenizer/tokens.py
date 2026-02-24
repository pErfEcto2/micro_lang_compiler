from abc import ABC


class Token(ABC):
    def __init__(self, line_num: int) -> None:
        super().__init__()
        self.line_number: int = line_num

class IDENTIFIER(Token):
    def __init__(self, line_num: int, val: str) -> None:
        super().__init__(line_num)
        self.val: str = val

    def __str__(self) -> str:
        return f"IDENTIFIER({self.val})"

    def __repr__(self) -> str:
        return str(self)
