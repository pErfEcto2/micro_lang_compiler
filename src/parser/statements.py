from parser.ast_node import ASTNode
from parser.expressions import EXPRESSION, IDENTIFIER_EXPRESSION


class STATEMENT(ASTNode):
    def __init__(self, line_number: int) -> None:
        self.line_number: int = line_number

    def __str__(self) -> str:
        return f"STATEMENT(line: {self.line_number})"

    def __repr__(self) -> str:
        return str(self)

class EXIT_STATEMENT(STATEMENT):
    def __init__(self, line_number: int, return_code: EXPRESSION) -> None:
        super().__init__(line_number)
        self.return_code: EXPRESSION = return_code

    def __str__(self) -> str:
        return f"EXIT_STATEMENT(ret: {self.return_code})"

class VARIABLE_TYPE(STATEMENT):
    def __init__(self, line_number: int, identifier: IDENTIFIER_EXPRESSION, expr: EXPRESSION) -> None:
        super().__init__(line_number)
        self.identifier: IDENTIFIER_EXPRESSION =  identifier
        self.expr: EXPRESSION = expr

class CONST_STATEMENT(STATEMENT):
    def __init__(self, line_number: int, var_statement: VARIABLE_TYPE) -> None:
        super().__init__(line_number)
        self.var_statement: VARIABLE_TYPE = var_statement

    def __str__(self) -> str:
        return f"CONST_{self.var_statement}"

class INT64_STATEMENT(VARIABLE_TYPE):
    def __init__(self, line_number: int, identifier: IDENTIFIER_EXPRESSION, expr: EXPRESSION) -> None:
        super().__init__(line_number, identifier, expr)

    def __str__(self) -> str:
        return f"INT64_STATEMENT(identifier: {self.identifier}, expr: {self.expr})"

class IF_STATEMENT(STATEMENT):
    def __init__(self, line_number: int, expr: EXPRESSION, true_body: list[STATEMENT], false_body: list[STATEMENT] | None = None) -> None:
        super().__init__(line_number)
        self.expr = expr
        self.true_body: list[STATEMENT] = true_body
        self.false_body: list[STATEMENT] | None = false_body

    def __str__(self) -> str:
        return f"IF_STATEMENT(expr: {self.expr}, true_body: {self.true_body}, false_body: {self.false_body})"

class WHILE_STATEMENT(STATEMENT):
    def __init__(self, line_number: int, expr: EXPRESSION, body: list[STATEMENT]) -> None:
        super().__init__(line_number)
        self.expr = expr
        self.body: list[STATEMENT] = body

    def __str__(self) -> str:
        return f"WHILE_STATEMENT(expr: {self.expr}, body: {self.body})"

class ASSIGN_STATEMENT(STATEMENT):
    def __init__(self, line_number: int, identifier: IDENTIFIER_EXPRESSION, expr: EXPRESSION) -> None:
        super().__init__(line_number)
        self.identifier: IDENTIFIER_EXPRESSION = identifier
        self.expr: EXPRESSION = expr

    def __str__(self) -> str:
        return f"ASSIGN_STATEMENT(identifier: {self.identifier}, expr: {self.expr})"

class OPEN_C_STATEMENT(STATEMENT):
    def __init__(self, line_number: int) -> None:
        super().__init__(line_number)

    def __str__(self) -> str:
        return "OPEN_C_STATEMENT"

class CLOSE_C_STATEMENT(STATEMENT):
    def __init__(self, line_number: int) -> None:
        super().__init__(line_number)

    def __str__(self) -> str:
        return "CLOSE_C_STATEMENT"

class PRINT_STATEMENT(STATEMENT):
    def __init__(self, line_number: int, expr: EXPRESSION) -> None:
        super().__init__(line_number)
        self.expr: EXPRESSION = expr

    def __str__(self) -> str:
        return f"PRINT_STATEMENT(expr: {self.expr})"
