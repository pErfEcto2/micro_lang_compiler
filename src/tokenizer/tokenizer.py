from tokenizer.tokens import Token


class Tokenizer:
    def __init__(self, src_code: str) -> None:
        self._src: str = src_code

    def tokenize(self) -> list[Token]:
        return []

