from parser.ast_node import ASTNode
from parser.expressions import EXPRESSION, IDENTIFIER_EXPRESSION
from tokenizer.keywords import UNARY_MATH_OPERATION


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
    def __init__(self, line_number: int, identifier: IDENTIFIER_EXPRESSION, expr: EXPRESSION, size: int) -> None:
        super().__init__(line_number)
        self.identifier: IDENTIFIER_EXPRESSION =  identifier
        self.expr: EXPRESSION = expr
        self.size: int = size

class CONST_STATEMENT(STATEMENT):
    def __init__(self, line_number: int, var_statement: VARIABLE_TYPE) -> None:
        super().__init__(line_number)
        self.var_statement: VARIABLE_TYPE = var_statement

    def __str__(self) -> str:
        return f"CONST_{self.var_statement}"

class INT64_STATEMENT(VARIABLE_TYPE):
    def __init__(self, line_number: int, identifier: IDENTIFIER_EXPRESSION, expr: EXPRESSION) -> None:
        super().__init__(line_number, identifier, expr, 8)

    def __str__(self) -> str:
        return f"INT64_STATEMENT(identifier: {self.identifier}, expr: {self.expr})"

class CHAR_STATEMENT(VARIABLE_TYPE):
    def __init__(self, line_number: int, identifier: IDENTIFIER_EXPRESSION, expr: EXPRESSION) -> None:
        super().__init__(line_number, identifier, expr, 1)

    def __str__(self) -> str:
        return f"CHAR_STATEMENT(identifier: {self.identifier}, expr: {self.expr})"

class IF_STATEMENT(STATEMENT):
    def __init__(self, line_number: int, expr: EXPRESSION, true_body: list[STATEMENT], false_body: list[STATEMENT] | None = None) -> None:
        super().__init__(line_number)
        self.expr = expr
        self.true_body: list[STATEMENT] = true_body
        self.false_body: list[STATEMENT] | None = false_body

    def __str__(self) -> str:
        return f"IF_STATEMENT(expr: {self.expr}, true_body: {self.true_body}, false_body: {self.false_body})"

class DO_WHILE_STATEMENT(STATEMENT):
    def __init__(self, line_number: int, expr: EXPRESSION, body: list[STATEMENT]) -> None:
        super().__init__(line_number)
        self.expr = expr
        self.body: list[STATEMENT] = body

    def __str__(self) -> str:
        return f"DO_WHILE_STATEMENT(expr: {self.expr}, body: {self.body})"

class WHILE_STATEMENT(STATEMENT):
    def __init__(self, line_number: int, expr: EXPRESSION, body: list[STATEMENT]) -> None:
        super().__init__(line_number)
        self.expr = expr
        self.body: list[STATEMENT] = body

    def __str__(self) -> str:
        return f"WHILE_STATEMENT(expr: {self.expr}, body: {self.body})"

class FOR_STATEMENT(STATEMENT):
    def __init__(self, line_number: int, body: list[STATEMENT], initialization: STATEMENT | None = None, condition: EXPRESSION | None = None, increment: STATEMENT | None = None) -> None:
        super().__init__(line_number)
        self.body: list[STATEMENT] = body
        self.initialization: STATEMENT | None = initialization
        self.condition: EXPRESSION | None = condition
        self.increment: STATEMENT | None = increment

    def __str__(self) -> str:
        return f"FOR_STATEMENT(body: {self.body}, init: {self.initialization}, condition: {self.condition}, increment: {self.increment})"

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

class POSTFIX_STATEMENT(STATEMENT):
    def __init__(self, line_number: int, identifier: IDENTIFIER_EXPRESSION, op: UNARY_MATH_OPERATION) -> None:
        super().__init__(line_number)
        self.identifier: IDENTIFIER_EXPRESSION = identifier
        self.op: UNARY_MATH_OPERATION = op

    def __str__(self) -> str:
        return f"POSTFIX_STATEMENT(identifier: {self.identifier}, op: {self.op})"

class PREFIX_STATEMENT(STATEMENT):
    def __init__(self, line_number: int, op: UNARY_MATH_OPERATION, identifier: IDENTIFIER_EXPRESSION) -> None:
        super().__init__(line_number)
        self.identifier: IDENTIFIER_EXPRESSION = identifier
        self.op: UNARY_MATH_OPERATION = op

    def __str__(self) -> str:
        return f"PREFIX_STATEMENT(op: {self.op}, identifier: {self.identifier})"

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
