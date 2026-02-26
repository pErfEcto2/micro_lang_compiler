from parser.ast_node import ASTNode
from parser.expressions import EXPRESSION, IDENTIFIER_EXPRESSION
from tokenizer.tokens import IDENTIFIER


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

class LET_STATEMENT(STATEMENT):
    def __init__(self, line_number: int, identifier: IDENTIFIER_EXPRESSION, expr: EXPRESSION) -> None:
        super().__init__(line_number)
        self.identifier: IDENTIFIER_EXPRESSION =  identifier
        self.expr: EXPRESSION = expr

    def __str__(self) -> str:
        return f"LET_STATEMENT(identifier: {self.identifier}, expr: {self.expr})"

    def __repr__(self) -> str:
        return str(self)

class ASSIGN_STATEMENT(STATEMENT):
    def __init__(self, line_number: int, identifier: IDENTIFIER_EXPRESSION, expr: EXPRESSION) -> None:
        super().__init__(line_number)
        self.identifier: IDENTIFIER_EXPRESSION = identifier
        self.expr: EXPRESSION = expr

    def __str__(self) -> str:
        return f"ASSIGN_STATEMENT(identifier: {self.identifier}, expr: {self.expr})"

    def __repr__(self) -> str:
        return str(self)

class PRINT_STATEMENT(STATEMENT):
    def __init__(self, line_number: int, expr: EXPRESSION) -> None:
        super().__init__(line_number)
        self.expr: EXPRESSION = expr

    def __str__(self) -> str:
        return f"PRINT_STATEMENT(expr: {self.expr})"

    def __repr__(self) -> str:
        return str(self)
