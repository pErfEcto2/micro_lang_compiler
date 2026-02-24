from parser.statements import EXIT_STATEMENT
from parser.program import PROGRAM
from parser.expressions import BINARY_EXPRESSION, EXPRESSION, INT_EXPRESSION, STR_EXPRESSION
from tokenizer.keywords import EXIT_KEYWORD, MATH_OPERATION, SEMICOLON
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

    def _check_current_token_type(self, t: type) -> bool:
        if self._peek() is None:
            raise ValueError(f"expected '{t}' at the end of the program")

        token = self._peek()
        return type(token) == t

    def _assert_current_token_type(self, t: type, err_msg: str | None = None) -> None:
        if not self._check_current_token_type(t):
            token = self._peek()
            raise ValueError(err_msg or f"expected '{t}' in line {token.line_number} ('{type(token)}' found)")

    def _parse_expr(self, token, min_bp: int = 0) -> EXPRESSION:
        ln = token.line_number

        match token:
            case INT_LITERAL():
                left = INT_EXPRESSION(ln, token.val)
                
                if not (self._peek() is not None and isinstance(self._peek(), MATH_OPERATION)):
                    return left

                while True:
                    op = self._peek()
                    if not isinstance(op, MATH_OPERATION) or op.bpower < min_bp:
                        break
                    
                    self._consume()
                    right = self._parse_expr(self._consume(), min_bp + 1)
                    left = BINARY_EXPRESSION(ln, left, op, right)
                
                return left
                
            case _:
                raise ValueError(f"unexpected expression '{token}' in line {ln}")

    def _parse_exit_statement(self) -> EXIT_STATEMENT:
        expr = self._parse_expr(self._consume())
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
