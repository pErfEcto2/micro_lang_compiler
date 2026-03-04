from parser.statements import ASSIGN_STATEMENT, CLOSE_C_STATEMENT, CONST_STATEMENT, EXIT_STATEMENT, IF_STATEMENT, INT64_STATEMENT, OPEN_C_STATEMENT, PRINT_STATEMENT, STATEMENT, WHILE_STATEMENT
from parser.program import PROGRAM
from parser.expressions import BINARY_EXPRESSION, EXPRESSION, IDENTIFIER_EXPRESSION, INT_EXPRESSION
from tokenizer.keywords import ASSIGN_KEYWORD, CLOSE_BRACKET, CLOSE_C_BRACKET, CONST_KEYWORD, ELSE_KEYWORD, EXIT_KEYWORD, IF_KEYWORD, INT64_KEYWORD, MATH_OPERATION, OPEN_BRACKET, OPEN_C_BRACKET, PRINT_KEYWORD, SEMICOLON, WHILE_KEYWORD
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
            right = self._parse_expr(self._consume(), op.bpower + 1)
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
        self._consume()
        return EXIT_STATEMENT(expr.line_number, expr)

    def _parse_int64_statement(self) -> INT64_STATEMENT:
        self._assert_current_token_type(IDENTIFIER)
        identifier = self._consume()
        identifier = IDENTIFIER_EXPRESSION(identifier.line_number, identifier.val)
        self._assert_current_token_type(ASSIGN_KEYWORD)
        self._consume()
        expr = self._parse_expr(self._consume())
        self._assert_current_token_type(SEMICOLON)
        self._consume()
        return INT64_STATEMENT(expr.line_number, identifier, expr)

    def _parse_print_statement(self) -> PRINT_STATEMENT:
        expr = self._parse_expr(self._consume())
        self._assert_current_token_type(SEMICOLON)
        self._consume()
        return PRINT_STATEMENT(expr.line_number, expr)

    def _parse_assign_statement(self, ln: int, name: str) -> ASSIGN_STATEMENT:
        self._assert_current_token_type(ASSIGN_KEYWORD)
        self._consume()
        identifier = IDENTIFIER_EXPRESSION(ln, name)
        expr = self._parse_expr(self._consume())
        self._assert_current_token_type(SEMICOLON)
        self._consume()
        return ASSIGN_STATEMENT(expr.line_number, identifier, expr)

    def _parse_const_statement(self, ln: int) -> CONST_STATEMENT:
        self._consume()
        return CONST_STATEMENT(ln, self._parse_int64_statement())

    def _parse_while_statement(self, ln: int) -> WHILE_STATEMENT:
        self._assert_current_token_type(OPEN_BRACKET)
        self._consume()
        
        expr = self._parse_expr(self._consume())
        
        self._assert_current_token_type(CLOSE_BRACKET)
        self._consume()
        
        self._assert_current_token_type(OPEN_C_BRACKET)
        self._consume()

        body = [OPEN_C_STATEMENT(ln)]
        while self._peek() is not None and type(self._peek()) != CLOSE_C_BRACKET:
            if (statement := self._create_statement(self._consume())) is not None:
                body.append(statement)

        body.append(CLOSE_C_STATEMENT(ln))

        self._assert_current_token_type(CLOSE_C_BRACKET)
        self._consume()

        return WHILE_STATEMENT(ln, expr, body)

    def _create_statement(self, token) -> STATEMENT | None:
        match token:
            case WHILE_KEYWORD():
                return self._parse_while_statement(token.line_number)
            case IF_KEYWORD():
                return self._parse_if_statement(token.line_number)
            case OPEN_C_BRACKET():
                return OPEN_C_STATEMENT(token.line_number)
            case CLOSE_C_BRACKET():
                return CLOSE_C_STATEMENT(token.line_number)
            case CONST_KEYWORD():
                return self._parse_const_statement(token.line_number)
            case IDENTIFIER():
                return self._parse_assign_statement(token.line_number, token.val)
            case EXIT_KEYWORD():
                return self._parse_exit_statement()
            case INT64_KEYWORD():
                return self._parse_int64_statement()
            case PRINT_KEYWORD():
                return self._parse_print_statement()
            case SEMICOLON():
                return
            case _:
                raise ValueError(f"unexpected token '{token}' in line {token.line_number}")

    def _parse_if_statement(self, ln: int) -> IF_STATEMENT:
        self._assert_current_token_type(OPEN_BRACKET)
        self._consume()

        expr = self._parse_expr(self._consume())
        
        self._assert_current_token_type(CLOSE_BRACKET)
        self._consume()

        self._assert_current_token_type(OPEN_C_BRACKET)

        true_body = []
        while self._peek() is not None and type(self._peek()) != CLOSE_C_BRACKET:
            if (statement := self._create_statement(self._consume())) is not None:
                true_body.append(statement)

        self._assert_current_token_type(CLOSE_C_BRACKET)
        true_body.append(self._create_statement(self._consume()))

        false_body = None
        if type(self._peek()) == ELSE_KEYWORD:
            self._consume()
            self._assert_current_token_type(OPEN_C_BRACKET)
            false_body = [self._create_statement(self._consume())]
            while self._peek() is not None and type(self._peek()) != CLOSE_C_BRACKET:
                if (statement := self._create_statement(self._consume())) is not None:
                    false_body.append(statement)
            self._assert_current_token_type(CLOSE_C_BRACKET)
            false_body.append(self._create_statement(self._consume()))

        return IF_STATEMENT(ln, expr, true_body, false_body)

    def parse(self) -> PROGRAM:
        program: PROGRAM = PROGRAM()
        while self._peek():
            token: Token = self._consume()
            if (statement := self._create_statement(token)) is not None:
                program.statements.append(statement)
        return program
