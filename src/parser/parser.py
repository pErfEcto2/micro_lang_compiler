from parser.statements import ASSIGN_STATEMENT, CHAR_STATEMENT, CLOSE_C_STATEMENT, CONST_STATEMENT, DO_WHILE_STATEMENT, EXIT_STATEMENT, FOR_STATEMENT, IF_STATEMENT, INT64_STATEMENT, OPEN_C_STATEMENT, POSTFIX_STATEMENT, PREFIX_STATEMENT, PRINT_STATEMENT, STATEMENT, WHILE_STATEMENT
from parser.program import PROGRAM
from parser.expressions import BINARY_EXPRESSION, CHAR_EXPRESSION, EXPRESSION, IDENTIFIER_EXPRESSION, INT_EXPRESSION, POSTFIX_EXPRESSION, PREFIX_EXPRESSION
from tokenizer.keywords import ASSIGN_KEYWORD, CHAR_KEYWORD, CLOSE_BRACKET, CLOSE_C_BRACKET, CONST_KEYWORD, DO_KEYWORD, ELSE_KEYWORD, EXIT_KEYWORD, FALSE_KEYWORD, FOR_KEYWORD, IF_KEYWORD, INT64_KEYWORD, MATH_OPERATION, MINUS_KEYWORD, MULTIPLY_KEYWORD, OPEN_BRACKET, OPEN_C_BRACKET, PRINT_KEYWORD, SEMICOLON, TRUE_KEYWORD, UNARY_MATH_OPERATION, WHILE_KEYWORD
from tokenizer.literals import CHAR_LITERAL, INT_LITERAL
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
            case MINUS_KEYWORD():
                return BINARY_EXPRESSION(ln, INT_EXPRESSION(ln, -1), MULTIPLY_KEYWORD(ln), self._parse_expr(self._consume()))
            case OPEN_BRACKET():
                expr = self._parse_expr(self._consume())
                self._assert_current_token_type(CLOSE_BRACKET)
                self._consume()
                return self._get_expr(expr, min_bp, ln)

            case INT_LITERAL():
                left = INT_EXPRESSION(ln, token.val)
                return self._get_expr(left, min_bp, ln)

            case UNARY_MATH_OPERATION():
                self._assert_current_token_type(IDENTIFIER)
                identifier = IDENTIFIER_EXPRESSION(ln, self._consume().val)
                left = PREFIX_EXPRESSION(ln, token, identifier)
                return self._get_expr(left, min_bp, ln)

            case IDENTIFIER():
                left = IDENTIFIER_EXPRESSION(ln, token.val)
                if isinstance(self._peek(), UNARY_MATH_OPERATION):
                    op = self._consume()
                    left = POSTFIX_EXPRESSION(ln, left, op)
                return self._get_expr(left, min_bp, ln)

            case CHAR_LITERAL():
                left = CHAR_EXPRESSION(ln, token.val)
                return self._get_expr(left, min_bp, ln)

            case TRUE_KEYWORD():
                left = INT_EXPRESSION(ln, 1)
                return self._get_expr(left, min_bp, ln)

            case FALSE_KEYWORD():
                left = INT_EXPRESSION(ln, 0)
                return self._get_expr(left, min_bp, ln)

            case _:
                raise ValueError(f"unexpected expression '{token}' in line {ln}")

    def _parse_body(self) -> list[STATEMENT]:
        self._assert_current_token_type(OPEN_C_BRACKET)                                                                                                                        
        body = [self._create_statement(self._consume())]                                                                                                                       
        c_bracket_cnt = 0                                                                                                                                                      
        while self._peek() is not None:                                                                                                                                        
            if isinstance(self._peek(), CLOSE_C_BRACKET) and c_bracket_cnt == 0:                                                                                               
                break                                                                                                                                                          
            statement = self._create_statement(self._consume())                                                                                                                
            if statement is not None:                                                                                                                                          
                if isinstance(statement, OPEN_C_STATEMENT):                                                                                                                    
                    c_bracket_cnt += 1                                                                                                                                         
                elif isinstance(statement, CLOSE_C_STATEMENT):                                                                                                                 
                    c_bracket_cnt -= 1                                                                                                                                         
                body.append(statement)                                                                                                                                         
        self._assert_current_token_type(CLOSE_C_BRACKET)                                                                                                                       
        body.append(self._create_statement(self._consume()))                                                                                                                   
        return body       

    def _parse_exit_statement(self) -> EXIT_STATEMENT:
        expr = self._parse_expr(self._consume())
        self._assert_current_token_type(SEMICOLON)
        self._consume()
        return EXIT_STATEMENT(expr.line_number, expr)

    def _parse_int64_statement(self, expect_semicolon: bool = True) -> INT64_STATEMENT:
        self._assert_current_token_type(IDENTIFIER)
        identifier = self._consume()
        identifier = IDENTIFIER_EXPRESSION(identifier.line_number, identifier.val)
        self._assert_current_token_type(ASSIGN_KEYWORD)
        self._consume()
        expr = self._parse_expr(self._consume())

        if expect_semicolon:
            self._assert_current_token_type(SEMICOLON)
            self._consume()
        return INT64_STATEMENT(expr.line_number, identifier, expr)

    def _parse_print_statement(self) -> PRINT_STATEMENT:
        expr = self._parse_expr(self._consume())
        self._assert_current_token_type(SEMICOLON)
        self._consume()
        return PRINT_STATEMENT(expr.line_number, expr)

    def _parse_assign_statement(self, ln: int, name: str, expect_semicolon: bool = True) -> ASSIGN_STATEMENT:
        self._assert_current_token_type(ASSIGN_KEYWORD)
        self._consume()
        identifier = IDENTIFIER_EXPRESSION(ln, name)
        expr = self._parse_expr(self._consume())

        if expect_semicolon:
            self._assert_current_token_type(SEMICOLON)
            self._consume()
        return ASSIGN_STATEMENT(expr.line_number, identifier, expr)

    def _parse_const_statement(self, ln: int) -> CONST_STATEMENT:
        t = self._consume()
        match t:
            case INT64_KEYWORD():
                return CONST_STATEMENT(ln, self._parse_int64_statement())
            case CHAR_KEYWORD():
                return CONST_STATEMENT(ln, self._parse_char_statement())
            case _:
                raise ValueError(f"unknown type '{type(t)}' in line {t.line_number}")

    def _parse_while_statement(self, ln: int) -> WHILE_STATEMENT:
        self._assert_current_token_type(OPEN_BRACKET)
        self._consume()
        
        expr = self._parse_expr(self._consume())
        
        self._assert_current_token_type(CLOSE_BRACKET)
        self._consume()
        
        body = self._parse_body()

        return WHILE_STATEMENT(ln, expr, body)

    def _parse_postfix_statement(self, ln: int, identifier_name: str, expect_semicolon: bool = True) -> POSTFIX_STATEMENT:
        op = self._consume()
        identifier = IDENTIFIER_EXPRESSION(ln, identifier_name)

        if expect_semicolon:
            self._assert_current_token_type(SEMICOLON)
            self._consume()
        return POSTFIX_STATEMENT(ln, identifier, op)

    def _parse_prefix_statement(self, ln: int, op: UNARY_MATH_OPERATION, expect_semicolon: bool = True) -> PREFIX_STATEMENT:
        self._assert_current_token_type(IDENTIFIER)
        name = self._consume().val
        identifier = IDENTIFIER_EXPRESSION(ln, name)
        
        if expect_semicolon:
            self._assert_current_token_type(SEMICOLON)
            self._consume()

        return PREFIX_STATEMENT(ln, op, identifier)

    def _parse_for_statement(self, ln: int) -> FOR_STATEMENT:
        self._assert_current_token_type(OPEN_BRACKET)
        self._consume()

        init = None
        if not isinstance(self._peek(), SEMICOLON):
            init = self._create_statement(self._consume())
        else:
            self._assert_current_token_type(SEMICOLON)
            self._consume()

        cond = None
        if not isinstance(self._peek(), SEMICOLON):
            cond = self._parse_expr(self._consume())

        self._assert_current_token_type(SEMICOLON)
        self._consume()

        inc = None
        if not isinstance(self._peek(), CLOSE_BRACKET):
            inc = self._create_statement(self._consume(), expect_semicolon=False)

        self._assert_current_token_type(CLOSE_BRACKET)
        self._consume()

        body = self._parse_body()

        return FOR_STATEMENT(ln, body, init, cond, inc)

    def _parse_char_statement(self, expect_semicolon: bool = True) -> CHAR_STATEMENT:
        self._assert_current_token_type(IDENTIFIER)
        identifier = self._consume()
        identifier = IDENTIFIER_EXPRESSION(identifier.line_number, identifier.val)
        self._assert_current_token_type(ASSIGN_KEYWORD)
        self._consume()

        expr = self._parse_expr(self._consume())
        
        if expect_semicolon:
            self._assert_current_token_type(SEMICOLON)
            self._consume()
        return CHAR_STATEMENT(expr.line_number, identifier, expr)

    def _parse_do_while_statement(self, ln: int) -> DO_WHILE_STATEMENT:
        body = self._parse_body()

        self._assert_current_token_type(WHILE_KEYWORD)
        self._consume()

        self._assert_current_token_type(OPEN_BRACKET)
        self._consume()

        expr = self._parse_expr(self._consume())

        self._assert_current_token_type(CLOSE_BRACKET)
        self._consume()

        self._assert_current_token_type(SEMICOLON)
        self._consume()

        return DO_WHILE_STATEMENT(ln, expr, body)

    def _create_statement(self, token, expect_semicolon: bool = True) -> STATEMENT | None:
        match token:
            case DO_KEYWORD():
                return self._parse_do_while_statement(token.line_number)
            case CHAR_KEYWORD():
                return self._parse_char_statement(expect_semicolon=expect_semicolon)
            case FOR_KEYWORD():
                return self._parse_for_statement(token.line_number)
            case UNARY_MATH_OPERATION():
                return self._parse_prefix_statement(token.line_number, token, expect_semicolon=expect_semicolon)
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
                if self._peek() is not None and isinstance(self._peek(), UNARY_MATH_OPERATION):
                    return self._parse_postfix_statement(token.line_number, token.val, expect_semicolon=expect_semicolon)
                else:
                    return self._parse_assign_statement(token.line_number, token.val, expect_semicolon=expect_semicolon)
            case EXIT_KEYWORD():
                return self._parse_exit_statement()
            case INT64_KEYWORD():
                return self._parse_int64_statement(expect_semicolon=expect_semicolon)
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

        true_body = self._parse_body()

        false_body = None
        if isinstance(self._peek(), ELSE_KEYWORD):
            self._consume()
            false_body = self._parse_body()

        return IF_STATEMENT(ln, expr, true_body, false_body)

    def parse(self) -> PROGRAM:
        program: PROGRAM = PROGRAM()
        while self._peek():
            token: Token = self._consume()
            if (statement := self._create_statement(token)) is not None:
                program.statements.append(statement)
        return program
