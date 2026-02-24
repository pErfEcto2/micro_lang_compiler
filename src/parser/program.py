from parser.ast_node import ASTNode
from parser.statements import STATEMENT


class PROGRAM(ASTNode):
    def __init__(self) -> None:
        self.statements: list[STATEMENT] = []

    def __str__(self) -> str:
        return f"PROGRAM:\n{self.statements}"

    def __repr__(self) -> str:
        return str(self)
