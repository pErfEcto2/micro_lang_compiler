from parser.ast_nodes import ASTNode
from tokenizer.tokens import Token


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens: list[Token] = tokens

    def parse(self) -> ASTNode | None:
        pass
