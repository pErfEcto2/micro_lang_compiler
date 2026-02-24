from parser.ast_node import ASTNode
from parser.expressions import EXPRESSION


class STATEMENT(ASTNode):
    def __init__(self, line_number: int) -> None:
        self.line_number: int = line_number

class EXIT_STATEMENT(STATEMENT):
    def __init__(self, line_number: int, return_code: EXPRESSION) -> None:
        super().__init__(line_number)
        self.return_code: EXPRESSION = return_code

    def __str__(self) -> str:
        return f"EXIT_STATEMENT(ret: {self.return_code})"

    def __repr__(self) -> str:
        return str(self)

