from parser.ast_node import ASTNode


class EXPRESSION(ASTNode):
    def __init__(self, line_number: int) -> None:
        super().__init__()
        self.line_number: int = line_number

class INT_EXPRESSION(EXPRESSION):
    def __init__(self, line_number: int, val: int) -> None:
        super().__init__(line_number)
        self.val: int = val

    def __str__(self) -> str:
        return f"INT_EXPRESSION({self.val})"

    def __repr__(self) -> str:
        return str(self)

class STR_EXPRESSION(EXPRESSION):
    def __init__(self, line_number: int, val: str) -> None:
        super().__init__(line_number)
        self.val: str = val

    def __str__(self) -> str:
        return f"STR_EXPRESSION({self.val})"

    def __repr__(self) -> str:
        return str(self)
