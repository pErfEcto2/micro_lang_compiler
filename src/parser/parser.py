from parser.statements import ASSIGN_STATEMENT, CONST_STATEMENT, EXIT_STATEMENT, INT64_STATEMENT, PRINT_STATEMENT
from parser.program import PROGRAM
from parser.expressions import BINARY_EXPRESSION, EXPRESSION, IDENTIFIER_EXPRESSION, INT_EXPRESSION
from tokenizer.keywords import ASSIGN_KEYWORD, CONST_KEYWORD, EXIT_KEYWORD, INT64_KEYWORD, MATH_OPERATION, PRINT_KEYWORD, SEMICOLON
from tokenizer.literals import INT_LITERAL
from tokenizer.tokens import IDENTIFIER, Token


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
    
    def _get_expr(self, left, min_bp, ln) -> EXPRESSION:
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

    def _parse_expr(self, token, min_bp: int = 0) -> EXPRESSION:
        ln = token.line_number
        match token:
            case INT_LITERAL():
                left = INT_EXPRESSION(ln, token.val)
                return self._get_expr(left, min_bp, ln)

            case IDENTIFIER():
                left = IDENTIFIER_EXPRESSION(ln, token.val)
                return self._get_expr(left, min_bp, ln)
                
            case _:
                raise ValueError(f"unexpected expression '{token}' in line {ln}")

    def _parse_exit_statement(self) -> EXIT_STATEMENT:
        expr = self._parse_expr(self._consume())
        self._assert_current_token_type(SEMICOLON)
        return EXIT_STATEMENT(expr.line_number, expr)

    def _parse_int64_statement(self) -> INT64_STATEMENT:
        self._assert_current_token_type(IDENTIFIER)
        identiefier = self._consume()
        identiefier = IDENTIFIER_EXPRESSION(identiefier.line_number, identiefier.val)
        self._assert_current_token_type(ASSIGN_KEYWORD)
        self._consume()
        expr = self._parse_expr(self._consume())
        self._assert_current_token_type(SEMICOLON)
        return INT64_STATEMENT(expr.line_number, identiefier, expr)

    def _parse_print_statement(self) -> PRINT_STATEMENT:
        expr = self._parse_expr(self._consume())
        self._assert_current_token_type(SEMICOLON)
        return PRINT_STATEMENT(expr.line_number, expr)

    def _parse_assign_statement(self, ln: int, name: str) -> ASSIGN_STATEMENT:
        self._assert_current_token_type(ASSIGN_KEYWORD)
        self._consume()
        identifier = IDENTIFIER_EXPRESSION(ln, name)
        expr = self._parse_expr(self._consume())
        return ASSIGN_STATEMENT(expr.line_number, identifier, expr)

    def _parse_const_statement(self, ln: int) -> CONST_STATEMENT:
        self._consume()
        return CONST_STATEMENT(ln, self._parse_int64_statement())

    def parse(self) -> PROGRAM:
        program: PROGRAM = PROGRAM()
        while self._peek():
            token: Token = self._consume()
            match token:
                case CONST_KEYWORD():
                    const_statement = self._parse_const_statement(token.line_number)
                    program.statements.append(const_statement)
                case IDENTIFIER():
                    assign_statemnt = self._parse_assign_statement(token.line_number, token.val)
                    program.statements.append(assign_statemnt)
                case EXIT_KEYWORD():
                    exit_statement = self._parse_exit_statement()
                    program.statements.append(exit_statement)
                case INT64_KEYWORD():
                    int64_statement = self._parse_int64_statement()
                    program.statements.append(int64_statement)
                case PRINT_KEYWORD():
                    print_statement = self._parse_print_statement()
                    program.statements.append(print_statement)
                case SEMICOLON():
                    continue
                case _:
                    raise ValueError(f"unexpected token '{token}' in line {token.line_number}")
        return program
