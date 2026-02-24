from parser.statements import EXIT_STATEMENT
from parser.program import PROGRAM
from parser.expressions import EXPRESSION, INT_EXPRESSION, STR_EXPRESSION
from tokenizer.keywords import EXIT_KEYWORD, SEMICOLON
from tokenizer.literals import INT_LITERAL, STR_LITERAL
from tokenizer.tokens import Token


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens: list[Token] = tokens
        self._idx: int = 0
        self._tokens_len: int = len(tokens)

    def _peek(self, offset: int = 0) -> Token | None:
        return self._tokens[self._idx + offset] if self._idx + offset < self._tokens_len else None

    def _consume(self) -> Token:
        self._idx += 1
        return self._tokens[self._idx - 1]

    def _assert_current_token_type(self, t: type, err_msg: str | None = None) -> None:
        if self._peek() is None:
            raise ValueError(f"expected '{t}' at the end of the program")

        token = self._consume()
        tt = type(token)
        if tt != t:
            raise ValueError(err_msg or f"expected '{t}' in line {token.line_number} ('{tt}' found)")

    def _parse_expr(self) -> EXPRESSION:
        token = self._consume()
        ln = token.line_number

        match token:
            case INT_LITERAL():
                return INT_EXPRESSION(ln, token.val)

            case STR_LITERAL():
                return STR_EXPRESSION(ln, token.val)

            case _:
                raise ValueError(f"unexpected expression '{token}' in line {token.line_number}")


    def _parse_exit_statement(self) -> EXIT_STATEMENT:
        expr = self._parse_expr()
        self._assert_current_token_type(SEMICOLON)
        return EXIT_STATEMENT(expr.line_number, expr)

    def parse(self) -> PROGRAM:
        program: PROGRAM = PROGRAM()
        while self._peek():
            token: Token = self._consume()
            match token:
                case EXIT_KEYWORD():
                    exit_statement = self._parse_exit_statement()
                    program.statements.append(exit_statement)
                case SEMICOLON():
                    continue
                case _:
                    raise ValueError(f"unexpected token '{token}' in line {token.line_number}")
        return program
