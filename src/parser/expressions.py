from parser.ast_node import ASTNode
from tokenizer.keywords import MATH_OPERATION, UNARY_MATH_OPERATION


class EXPRESSION(ASTNode):
    def __init__(self, line_number: int) -> None:
        super().__init__()
        self.line_number: int = line_number

    def __repr__(self) -> str:
        return str(self)

class INT_EXPRESSION(EXPRESSION):
    def __init__(self, line_number: int, val: int) -> None:
        super().__init__(line_number)
        self.val: int = val

    def __str__(self) -> str:
        return f"{self.val}"

class STR_EXPRESSION(EXPRESSION):
    def __init__(self, line_number: int, val: str) -> None:
        super().__init__(line_number)
        self.val: str = val

    def __str__(self) -> str:
        return f"{self.val}"

class BINARY_EXPRESSION(EXPRESSION):
    def __init__(self, line_number: int, lval: EXPRESSION, op: MATH_OPERATION, rval: EXPRESSION) -> None:
        super().__init__(line_number)
        self.lval: EXPRESSION = lval
        self.rval: EXPRESSION = rval
        self.op: MATH_OPERATION = op

    def __str__(self) -> str:
        return f"{self.lval} {self.op} {self.rval}"

class IDENTIFIER_EXPRESSION(EXPRESSION):
    def __init__(self, line_number: int, identifier: str) -> None:
        super().__init__(line_number)
        self.name: str = identifier

    def __str__(self) -> str:
        return f"{self.name}"

class UNARY_EXPRESSION(EXPRESSION):
    def __init__(self, line_number: int, op: UNARY_MATH_OPERATION, identifier: IDENTIFIER_EXPRESSION) -> None:
        super().__init__(line_number)
        self.op: UNARY_MATH_OPERATION = op
        self.identifier: IDENTIFIER_EXPRESSION = identifier

class PREFIX_EXPRESSION(UNARY_EXPRESSION):
    def __init__(self, line_number: int, op: UNARY_MATH_OPERATION, identifier: IDENTIFIER_EXPRESSION) -> None:
        super().__init__(line_number, op, identifier)

    def __str__(self) -> str:
        return f"{self.op} {self.identifier}"

class POSTFIX_EXPRESSION(UNARY_EXPRESSION):
    def __init__(self, line_number: int, identifier: IDENTIFIER_EXPRESSION, op: UNARY_MATH_OPERATION) -> None:
        super().__init__(line_number, op, identifier)

    def __str__(self) -> str:
        return f"{self.identifier} {self.op}"

