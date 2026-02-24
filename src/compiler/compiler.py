from parser.ast_node import ASTNode


class Compiler:
    def __init__(self, ast_tree: ASTNode) -> None:
        self._ast: ASTNode = ast_tree

    def compile(self) -> str | None:
        pass

