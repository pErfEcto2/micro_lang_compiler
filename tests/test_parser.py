import pytest
from parser.parser import Parser
from parser.program import PROGRAM
from parser.statements import ASSIGN_STATEMENT, CLOSE_C_STATEMENT, CONST_STATEMENT, EXIT_STATEMENT, IF_STATEMENT, INT64_STATEMENT, OPEN_C_STATEMENT, PRINT_STATEMENT
from parser.expressions import BINARY_EXPRESSION, IDENTIFIER_EXPRESSION, INT_EXPRESSION, STR_EXPRESSION
from tokenizer.keywords import ASSIGN_KEYWORD, CLOSE_BRACKET, CLOSE_C_BRACKET, CONST_KEYWORD, ELSE_KEYWORD, EXIT_KEYWORD, IF_KEYWORD, INT64_KEYWORD, MINUS_KEYWORD, MULTIPLY_KEYWORD, OPEN_BRACKET, OPEN_C_BRACKET, PLUS_KEYWORD, PRINT_KEYWORD, SEMICOLON
from tokenizer.literals import INT_LITERAL, STR_LITERAL
from tokenizer.tokens import IDENTIFIER


class TestParserEmptyInput:
    def test_empty_token_list(self):
        program = Parser([]).parse()
        assert isinstance(program, PROGRAM)
        assert program.statements == []

    def test_semicolons_only(self):
        tokens = [SEMICOLON(1), SEMICOLON(1), SEMICOLON(1)]
        program = Parser(tokens).parse()
        assert isinstance(program, PROGRAM)
        assert program.statements == []


class TestParserExitStatement:
    def test_exit_with_int(self):
        tokens = [EXIT_KEYWORD(1), INT_LITERAL(1, 69), SEMICOLON(1)]
        program = Parser(tokens).parse()
        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, EXIT_STATEMENT)
        assert isinstance(stmt.return_code, INT_EXPRESSION)
        assert stmt.return_code.val == 69

    def test_exit_with_zero(self):
        tokens = [EXIT_KEYWORD(1), INT_LITERAL(1, 0), SEMICOLON(1)]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert isinstance(stmt, EXIT_STATEMENT)
        assert stmt.return_code.val == 0

    def test_exit_with_large_int(self):
        tokens = [EXIT_KEYWORD(1), INT_LITERAL(1, 999999), SEMICOLON(1)]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert stmt.return_code.val == 999999

    def test_exit_with_str_raises(self):
        tokens = [EXIT_KEYWORD(1), STR_LITERAL(1, "hello"), SEMICOLON(1)]
        with pytest.raises(ValueError, match="unexpected expression"):
            Parser(tokens).parse()

    def test_exit_preserves_line_number(self):
        tokens = [EXIT_KEYWORD(5), INT_LITERAL(5, 1), SEMICOLON(5)]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert stmt.return_code.line_number == 5


class TestParserMultipleStatements:
    def test_two_exit_statements(self):
        tokens = [
            EXIT_KEYWORD(1), INT_LITERAL(1, 69), SEMICOLON(1),
            EXIT_KEYWORD(2), INT_LITERAL(2, 70), SEMICOLON(2),
        ]
        program = Parser(tokens).parse()
        assert len(program.statements) == 2
        assert isinstance(program.statements[0], EXIT_STATEMENT)
        assert isinstance(program.statements[1], EXIT_STATEMENT)
        assert program.statements[0].return_code.val == 69
        assert program.statements[1].return_code.val == 70

    def test_three_exit_statements(self):
        tokens = [
            EXIT_KEYWORD(1), INT_LITERAL(1, 1), SEMICOLON(1),
            EXIT_KEYWORD(2), INT_LITERAL(2, 2), SEMICOLON(2),
            EXIT_KEYWORD(3), INT_LITERAL(3, 3), SEMICOLON(3),
        ]
        program = Parser(tokens).parse()
        assert len(program.statements) == 3
        for i, stmt in enumerate(program.statements):
            assert stmt.return_code.val == i + 1

    def test_statements_with_extra_semicolons(self):
        tokens = [
            SEMICOLON(1),
            EXIT_KEYWORD(1), INT_LITERAL(1, 42), SEMICOLON(1),
            SEMICOLON(2),
            SEMICOLON(2),
            EXIT_KEYWORD(2), INT_LITERAL(2, 0), SEMICOLON(2),
            SEMICOLON(3),
        ]
        program = Parser(tokens).parse()
        assert len(program.statements) == 2
        assert program.statements[0].return_code.val == 42
        assert program.statements[1].return_code.val == 0


class TestParserErrors:
    def test_identifier_without_assign_raises(self):
        tokens = [IDENTIFIER(1, "foo"), SEMICOLON(1)]
        with pytest.raises(ValueError, match="expected"):
            Parser(tokens).parse()

    def test_unexpected_token_int_literal(self):
        tokens = [INT_LITERAL(1, 42)]
        with pytest.raises(ValueError, match="unexpected token"):
            Parser(tokens).parse()

    def test_exit_missing_semicolon(self):
        tokens = [EXIT_KEYWORD(1), INT_LITERAL(1, 69)]
        with pytest.raises(ValueError, match="expected"):
            Parser(tokens).parse()

    def test_exit_wrong_terminator(self):
        tokens = [EXIT_KEYWORD(1), INT_LITERAL(1, 69), EXIT_KEYWORD(1)]
        with pytest.raises(ValueError, match="expected"):
            Parser(tokens).parse()

    def test_exit_without_expression(self):
        tokens = [EXIT_KEYWORD(1), SEMICOLON(1)]
        with pytest.raises(ValueError, match="unexpected expression"):
            Parser(tokens).parse()

    def test_identifier_expression_now_valid(self):
        tokens = [EXIT_KEYWORD(1), IDENTIFIER(1, "x"), SEMICOLON(1)]
        program = Parser(tokens).parse()
        expr = program.statements[0].return_code
        assert isinstance(expr, IDENTIFIER_EXPRESSION)
        assert expr.name == "x"

    def test_error_reports_line_number(self):
        tokens = [INT_LITERAL(7, 42)]
        with pytest.raises(ValueError, match="line 7"):
            Parser(tokens).parse()

    def test_exit_with_str_expression_error_reports_line(self):
        tokens = [EXIT_KEYWORD(3), STR_LITERAL(3, "x"), SEMICOLON(3)]
        with pytest.raises(ValueError, match="line 3"):
            Parser(tokens).parse()


class TestParserExpressions:
    def test_int_expression_value(self):
        tokens = [EXIT_KEYWORD(1), INT_LITERAL(1, 255), SEMICOLON(1)]
        program = Parser(tokens).parse()
        expr = program.statements[0].return_code
        assert isinstance(expr, INT_EXPRESSION)
        assert expr.val == 255
        assert expr.line_number == 1

    def test_str_expression_raises(self):
        tokens = [EXIT_KEYWORD(1), STR_LITERAL(1, "world"), SEMICOLON(1)]
        with pytest.raises(ValueError, match="unexpected expression"):
            Parser(tokens).parse()

    def test_int_expression_repr(self):
        expr = INT_EXPRESSION(1, 42)
        assert repr(expr) == "42"

    def test_str_expression_repr(self):
        expr = STR_EXPRESSION(1, "hello")
        assert repr(expr) == "hello"

    def test_str_expression_str(self):
        expr = STR_EXPRESSION(1, "world")
        assert str(expr) == "world"


class TestParserProgramRepr:
    def test_program_str(self):
        program = PROGRAM()
        assert "PROGRAM" in str(program)

    def test_program_repr(self):
        program = PROGRAM()
        assert repr(program) == str(program)

    def test_exit_statement_repr(self):
        tokens = [EXIT_KEYWORD(1), INT_LITERAL(1, 42), SEMICOLON(1)]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert "EXIT_STATEMENT" in repr(stmt)


class TestParserIntegration:
    """Tests that run tokenizer + parser together."""

    def test_full_pipeline_exit(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("exit 69;").tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 1
        assert isinstance(program.statements[0], EXIT_STATEMENT)
        assert program.statements[0].return_code.val == 69

    def test_full_pipeline_multiple_exits(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("exit 69;\nexit 70;").tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 2
        assert program.statements[0].return_code.val == 69
        assert program.statements[1].return_code.val == 70

    def test_full_pipeline_empty(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("").tokenize()
        program = Parser(tokens).parse()
        assert program.statements == []

    def test_full_pipeline_identifier_without_assign_fails(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("foo;").tokenize()
        with pytest.raises(ValueError, match="expected"):
            Parser(tokens).parse()

    def test_full_pipeline_arithmetic(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("exit 1 + 2;").tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 1
        expr = program.statements[0].return_code
        assert isinstance(expr, BINARY_EXPRESSION)

    def test_full_pipeline_int64_statement(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("int64 x = 5;").tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 1
        assert isinstance(program.statements[0], INT64_STATEMENT)

    def test_full_pipeline_int64_and_exit(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("int64 x = 5;\nexit x;").tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 2
        assert isinstance(program.statements[0], INT64_STATEMENT)
        assert isinstance(program.statements[1], EXIT_STATEMENT)

    def test_full_pipeline_subtraction(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("exit 10 - 3;").tokenize()
        program = Parser(tokens).parse()
        expr = program.statements[0].return_code
        assert isinstance(expr, BINARY_EXPRESSION)


class TestParserInt64Statement:
    def test_simple_int64(self):
        tokens = [
            INT64_KEYWORD(1), IDENTIFIER(1, "x"), ASSIGN_KEYWORD(1),
            INT_LITERAL(1, 5), SEMICOLON(1),
        ]
        program = Parser(tokens).parse()
        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, INT64_STATEMENT)
        assert stmt.identifier.name == "x"
        assert isinstance(stmt.expr, INT_EXPRESSION)
        assert stmt.expr.val == 5

    def test_int64_with_expression(self):
        tokens = [
            INT64_KEYWORD(1), IDENTIFIER(1, "y"), ASSIGN_KEYWORD(1),
            INT_LITERAL(1, 1), PLUS_KEYWORD(1), INT_LITERAL(1, 2), SEMICOLON(1),
        ]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert isinstance(stmt, INT64_STATEMENT)
        assert isinstance(stmt.expr, BINARY_EXPRESSION)

    def test_int64_missing_identifier(self):
        tokens = [INT64_KEYWORD(1), INT_LITERAL(1, 5), ASSIGN_KEYWORD(1), INT_LITERAL(1, 5), SEMICOLON(1)]
        with pytest.raises(ValueError, match="expected"):
            Parser(tokens).parse()

    def test_int64_missing_assign(self):
        tokens = [INT64_KEYWORD(1), IDENTIFIER(1, "x"), INT_LITERAL(1, 5), SEMICOLON(1)]
        with pytest.raises(ValueError, match="expected"):
            Parser(tokens).parse()

    def test_int64_missing_semicolon(self):
        tokens = [INT64_KEYWORD(1), IDENTIFIER(1, "x"), ASSIGN_KEYWORD(1), INT_LITERAL(1, 5)]
        with pytest.raises(ValueError, match="expected"):
            Parser(tokens).parse()

    def test_int64_repr(self):
        stmt = INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5))
        assert "INT64_STATEMENT" in repr(stmt)
        assert "x" in repr(stmt)

    def test_int64_preserves_line_number(self):
        tokens = [
            INT64_KEYWORD(3), IDENTIFIER(3, "z"), ASSIGN_KEYWORD(3),
            INT_LITERAL(3, 10), SEMICOLON(3),
        ]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert stmt.line_number == 3


class TestParserConstStatement:
    def test_simple_const(self):
        tokens = [
            CONST_KEYWORD(1), INT64_KEYWORD(1), IDENTIFIER(1, "x"), ASSIGN_KEYWORD(1),
            INT_LITERAL(1, 5), SEMICOLON(1),
        ]
        program = Parser(tokens).parse()
        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, CONST_STATEMENT)
        assert isinstance(stmt.var_statement, INT64_STATEMENT)
        assert stmt.var_statement.identifier.name == "x"
        assert stmt.var_statement.expr.val == 5

    def test_const_with_expression(self):
        tokens = [
            CONST_KEYWORD(1), INT64_KEYWORD(1), IDENTIFIER(1, "y"), ASSIGN_KEYWORD(1),
            INT_LITERAL(1, 1), PLUS_KEYWORD(1), INT_LITERAL(1, 2), SEMICOLON(1),
        ]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert isinstance(stmt, CONST_STATEMENT)
        assert isinstance(stmt.var_statement.expr, BINARY_EXPRESSION)

    def test_const_repr(self):
        inner = INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5))
        stmt = CONST_STATEMENT(1, inner)
        assert "CONST" in repr(stmt)

    def test_full_pipeline_const(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("const int64 x = 5;").tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 1
        assert isinstance(program.statements[0], CONST_STATEMENT)


class TestParserIdentifierExpression:
    def test_exit_with_identifier(self):
        tokens = [EXIT_KEYWORD(1), IDENTIFIER(1, "x"), SEMICOLON(1)]
        program = Parser(tokens).parse()
        expr = program.statements[0].return_code
        assert isinstance(expr, IDENTIFIER_EXPRESSION)
        assert expr.name == "x"

    def test_identifier_in_binary_expr(self):
        tokens = [
            EXIT_KEYWORD(1), IDENTIFIER(1, "a"), PLUS_KEYWORD(1), INT_LITERAL(1, 1), SEMICOLON(1),
        ]
        program = Parser(tokens).parse()
        expr = program.statements[0].return_code
        assert isinstance(expr, BINARY_EXPRESSION)
        assert isinstance(expr.lval, IDENTIFIER_EXPRESSION)
        assert expr.lval.name == "a"

    def test_identifier_expression_repr(self):
        expr = IDENTIFIER_EXPRESSION(1, "foo")
        assert repr(expr) == "foo"


class TestParserBinaryExpressions:
    def test_simple_addition(self):
        tokens = [EXIT_KEYWORD(1), INT_LITERAL(1, 1), PLUS_KEYWORD(1), INT_LITERAL(1, 2), SEMICOLON(1)]
        program = Parser(tokens).parse()
        expr = program.statements[0].return_code
        assert isinstance(expr, BINARY_EXPRESSION)
        assert expr.lval.val == 1
        assert expr.rval.val == 2

    def test_simple_multiplication(self):
        tokens = [EXIT_KEYWORD(1), INT_LITERAL(1, 3), MULTIPLY_KEYWORD(1), INT_LITERAL(1, 4), SEMICOLON(1)]
        program = Parser(tokens).parse()
        expr = program.statements[0].return_code
        assert isinstance(expr, BINARY_EXPRESSION)
        assert expr.lval.val == 3
        assert expr.rval.val == 4

    def test_simple_subtraction(self):
        tokens = [EXIT_KEYWORD(1), INT_LITERAL(1, 10), MINUS_KEYWORD(1), INT_LITERAL(1, 3), SEMICOLON(1)]
        program = Parser(tokens).parse()
        expr = program.statements[0].return_code
        assert isinstance(expr, BINARY_EXPRESSION)
        assert expr.lval.val == 10
        assert expr.rval.val == 3

    def test_multiply_binds_tighter_than_add(self):
        # 1 + 2 * 3 → BINARY(1, +, BINARY(2, *, 3))
        tokens = [
            EXIT_KEYWORD(1),
            INT_LITERAL(1, 1), PLUS_KEYWORD(1), INT_LITERAL(1, 2), MULTIPLY_KEYWORD(1), INT_LITERAL(1, 3),
            SEMICOLON(1),
        ]
        program = Parser(tokens).parse()
        expr = program.statements[0].return_code
        assert isinstance(expr, BINARY_EXPRESSION)
        assert isinstance(expr.lval, INT_EXPRESSION)
        assert expr.lval.val == 1
        assert isinstance(expr.rval, BINARY_EXPRESSION)
        assert expr.rval.lval.val == 2
        assert expr.rval.rval.val == 3

    def test_subtract_same_precedence_as_add(self):
        # 5 - 3 + 1 → BINARY(5, -, BINARY(3, +, 1)) (right-associative with min_bp + 1)
        tokens = [
            EXIT_KEYWORD(1),
            INT_LITERAL(1, 5), MINUS_KEYWORD(1), INT_LITERAL(1, 3), PLUS_KEYWORD(1), INT_LITERAL(1, 1),
            SEMICOLON(1),
        ]
        program = Parser(tokens).parse()
        expr = program.statements[0].return_code
        assert isinstance(expr, BINARY_EXPRESSION)
        assert isinstance(expr.lval, INT_EXPRESSION)
        assert expr.lval.val == 5
        assert isinstance(expr.rval, BINARY_EXPRESSION)
        assert expr.rval.lval.val == 3
        assert expr.rval.rval.val == 1

    def test_binary_expression_repr(self):
        expr = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 10), PLUS_KEYWORD(1), INT_EXPRESSION(1, 20))
        assert repr(expr) == "10 + 20"


class TestParserPrintStatement:
    def test_simple_print(self):
        tokens = [PRINT_KEYWORD(1), INT_LITERAL(1, 42), SEMICOLON(1)]
        program = Parser(tokens).parse()
        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, PRINT_STATEMENT)
        assert isinstance(stmt.expr, INT_EXPRESSION)
        assert stmt.expr.val == 42

    def test_print_identifier(self):
        tokens = [PRINT_KEYWORD(1), IDENTIFIER(1, "x"), SEMICOLON(1)]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert isinstance(stmt, PRINT_STATEMENT)
        assert isinstance(stmt.expr, IDENTIFIER_EXPRESSION)
        assert stmt.expr.name == "x"

    def test_print_expression(self):
        tokens = [
            PRINT_KEYWORD(1), INT_LITERAL(1, 1), PLUS_KEYWORD(1), INT_LITERAL(1, 2), SEMICOLON(1),
        ]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert isinstance(stmt, PRINT_STATEMENT)
        assert isinstance(stmt.expr, BINARY_EXPRESSION)

    def test_print_missing_semicolon(self):
        tokens = [PRINT_KEYWORD(1), INT_LITERAL(1, 42)]
        with pytest.raises(ValueError, match="expected"):
            Parser(tokens).parse()

    def test_print_repr(self):
        stmt = PRINT_STATEMENT(1, INT_EXPRESSION(1, 42))
        assert "PRINT_STATEMENT" in repr(stmt)

    def test_full_pipeline_print(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("print 42;").tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 1
        assert isinstance(program.statements[0], PRINT_STATEMENT)

    def test_full_pipeline_int64_and_print(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("int64 x = 5;\nprint x;").tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 2
        assert isinstance(program.statements[0], INT64_STATEMENT)
        assert isinstance(program.statements[1], PRINT_STATEMENT)


class TestParserAssignStatement:
    def test_simple_assign(self):
        tokens = [
            IDENTIFIER(1, "x"), ASSIGN_KEYWORD(1), INT_LITERAL(1, 10), SEMICOLON(1),
        ]
        program = Parser(tokens).parse()
        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, ASSIGN_STATEMENT)
        assert stmt.identifier.name == "x"
        assert isinstance(stmt.expr, INT_EXPRESSION)
        assert stmt.expr.val == 10

    def test_assign_with_expression(self):
        tokens = [
            IDENTIFIER(1, "x"), ASSIGN_KEYWORD(1),
            INT_LITERAL(1, 1), PLUS_KEYWORD(1), INT_LITERAL(1, 2), SEMICOLON(1),
        ]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert isinstance(stmt, ASSIGN_STATEMENT)
        assert isinstance(stmt.expr, BINARY_EXPRESSION)

    def test_assign_repr(self):
        stmt = ASSIGN_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5))
        assert "ASSIGN_STATEMENT" in repr(stmt)
        assert "x" in repr(stmt)

    def test_full_pipeline_assign(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("x = 10;").tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 1
        assert isinstance(program.statements[0], ASSIGN_STATEMENT)

    def test_full_pipeline_int64_assign_exit(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("int64 x = 1;\nx = 10;\nexit x;").tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 3
        assert isinstance(program.statements[0], INT64_STATEMENT)
        assert isinstance(program.statements[1], ASSIGN_STATEMENT)
        assert isinstance(program.statements[2], EXIT_STATEMENT)


class TestParserScopeStatements:
    def test_empty_scope(self):
        tokens = [OPEN_C_BRACKET(1), CLOSE_C_BRACKET(1)]
        program = Parser(tokens).parse()
        assert len(program.statements) == 2
        assert isinstance(program.statements[0], OPEN_C_STATEMENT)
        assert isinstance(program.statements[1], CLOSE_C_STATEMENT)

    def test_scope_with_statement(self):
        tokens = [
            OPEN_C_BRACKET(1),
            INT64_KEYWORD(2), IDENTIFIER(2, "x"), ASSIGN_KEYWORD(2),
            INT_LITERAL(2, 5), SEMICOLON(2),
            CLOSE_C_BRACKET(3),
        ]
        program = Parser(tokens).parse()
        assert len(program.statements) == 3
        assert isinstance(program.statements[0], OPEN_C_STATEMENT)
        assert isinstance(program.statements[1], INT64_STATEMENT)
        assert isinstance(program.statements[2], CLOSE_C_STATEMENT)

    def test_scope_preserves_line_numbers(self):
        tokens = [OPEN_C_BRACKET(5), CLOSE_C_BRACKET(10)]
        program = Parser(tokens).parse()
        assert program.statements[0].line_number == 5
        assert program.statements[1].line_number == 10

    def test_nested_scopes(self):
        tokens = [
            OPEN_C_BRACKET(1), OPEN_C_BRACKET(2),
            CLOSE_C_BRACKET(3), CLOSE_C_BRACKET(4),
        ]
        program = Parser(tokens).parse()
        assert len(program.statements) == 4
        assert isinstance(program.statements[0], OPEN_C_STATEMENT)
        assert isinstance(program.statements[1], OPEN_C_STATEMENT)
        assert isinstance(program.statements[2], CLOSE_C_STATEMENT)
        assert isinstance(program.statements[3], CLOSE_C_STATEMENT)

    def test_scope_repr(self):
        assert "OPEN_C_STATEMENT" in repr(OPEN_C_STATEMENT(1))
        assert "CLOSE_C_STATEMENT" in repr(CLOSE_C_STATEMENT(1))

    def test_full_pipeline_scope(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("{ int64 x = 5; }").tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 3
        assert isinstance(program.statements[0], OPEN_C_STATEMENT)
        assert isinstance(program.statements[1], INT64_STATEMENT)
        assert isinstance(program.statements[2], CLOSE_C_STATEMENT)

    def test_full_pipeline_nested_scope(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("int64 a = 1;\n{ int64 b = 2; }\nprint a;").tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 5
        assert isinstance(program.statements[0], INT64_STATEMENT)
        assert isinstance(program.statements[1], OPEN_C_STATEMENT)
        assert isinstance(program.statements[2], INT64_STATEMENT)
        assert isinstance(program.statements[3], CLOSE_C_STATEMENT)
        assert isinstance(program.statements[4], PRINT_STATEMENT)


class TestParserIfStatement:
    def test_simple_if(self):
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1), INT_LITERAL(1, 1), CLOSE_BRACKET(1),
            OPEN_C_BRACKET(1), PRINT_KEYWORD(1), INT_LITERAL(1, 42), SEMICOLON(1),
            CLOSE_C_BRACKET(1),
        ]
        program = Parser(tokens).parse()
        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, IF_STATEMENT)
        assert isinstance(stmt.expr, INT_EXPRESSION)
        assert stmt.expr.val == 1
        assert stmt.false_body is None

    def test_if_has_scope_in_body(self):
        """if body includes OPEN_C_STATEMENT and CLOSE_C_STATEMENT for scoping"""
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1), INT_LITERAL(1, 1), CLOSE_BRACKET(1),
            OPEN_C_BRACKET(1), PRINT_KEYWORD(2), INT_LITERAL(2, 42), SEMICOLON(2),
            CLOSE_C_BRACKET(3),
        ]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert isinstance(stmt.true_body[0], OPEN_C_STATEMENT)
        assert isinstance(stmt.true_body[-1], CLOSE_C_STATEMENT)

    def test_if_body_statements(self):
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1), INT_LITERAL(1, 1), CLOSE_BRACKET(1),
            OPEN_C_BRACKET(1),
            PRINT_KEYWORD(2), INT_LITERAL(2, 10), SEMICOLON(2),
            PRINT_KEYWORD(3), INT_LITERAL(3, 20), SEMICOLON(3),
            CLOSE_C_BRACKET(4),
        ]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        # body: OPEN_C, PRINT, PRINT, CLOSE_C
        assert len(stmt.true_body) == 4
        assert isinstance(stmt.true_body[1], PRINT_STATEMENT)
        assert isinstance(stmt.true_body[2], PRINT_STATEMENT)

    def test_if_with_identifier_condition(self):
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1), IDENTIFIER(1, "x"), CLOSE_BRACKET(1),
            OPEN_C_BRACKET(1), PRINT_KEYWORD(2), INT_LITERAL(2, 1), SEMICOLON(2),
            CLOSE_C_BRACKET(3),
        ]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert isinstance(stmt.expr, IDENTIFIER_EXPRESSION)
        assert stmt.expr.name == "x"

    def test_if_with_binary_condition(self):
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1),
            INT_LITERAL(1, 1), PLUS_KEYWORD(1), INT_LITERAL(1, 2),
            CLOSE_BRACKET(1),
            OPEN_C_BRACKET(1), PRINT_KEYWORD(2), INT_LITERAL(2, 1), SEMICOLON(2),
            CLOSE_C_BRACKET(3),
        ]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert isinstance(stmt.expr, BINARY_EXPRESSION)

    def test_if_preserves_line_number(self):
        tokens = [
            IF_KEYWORD(5), OPEN_BRACKET(5), INT_LITERAL(5, 1), CLOSE_BRACKET(5),
            OPEN_C_BRACKET(5), CLOSE_C_BRACKET(6),
        ]
        program = Parser(tokens).parse()
        assert program.statements[0].line_number == 5

    def test_if_empty_body(self):
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1), INT_LITERAL(1, 1), CLOSE_BRACKET(1),
            OPEN_C_BRACKET(1), CLOSE_C_BRACKET(1),
        ]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert isinstance(stmt, IF_STATEMENT)
        # body only has OPEN_C and CLOSE_C
        assert len(stmt.true_body) == 2
        assert isinstance(stmt.true_body[0], OPEN_C_STATEMENT)
        assert isinstance(stmt.true_body[1], CLOSE_C_STATEMENT)

    def test_if_repr(self):
        stmt = IF_STATEMENT(1, INT_EXPRESSION(1, 1), [], None)
        assert "IF_STATEMENT" in repr(stmt)

    def test_if_missing_open_paren(self):
        tokens = [
            IF_KEYWORD(1), INT_LITERAL(1, 1), CLOSE_BRACKET(1),
            OPEN_C_BRACKET(1), CLOSE_C_BRACKET(1),
        ]
        with pytest.raises(ValueError, match="expected"):
            Parser(tokens).parse()

    def test_if_missing_close_paren(self):
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1), INT_LITERAL(1, 1),
            OPEN_C_BRACKET(1), CLOSE_C_BRACKET(1),
        ]
        with pytest.raises(ValueError, match="expected"):
            Parser(tokens).parse()

    def test_if_missing_open_brace(self):
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1), INT_LITERAL(1, 1), CLOSE_BRACKET(1),
            PRINT_KEYWORD(1), INT_LITERAL(1, 1), SEMICOLON(1),
        ]
        with pytest.raises(ValueError, match="expected"):
            Parser(tokens).parse()

    def test_if_followed_by_other_statements(self):
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1), INT_LITERAL(1, 1), CLOSE_BRACKET(1),
            OPEN_C_BRACKET(1), PRINT_KEYWORD(2), INT_LITERAL(2, 1), SEMICOLON(2),
            CLOSE_C_BRACKET(3),
            PRINT_KEYWORD(4), INT_LITERAL(4, 99), SEMICOLON(4),
        ]
        program = Parser(tokens).parse()
        assert len(program.statements) == 2
        assert isinstance(program.statements[0], IF_STATEMENT)
        assert isinstance(program.statements[1], PRINT_STATEMENT)
        assert program.statements[1].expr.val == 99


class TestParserIfElseStatement:
    def test_simple_if_else(self):
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1), INT_LITERAL(1, 0), CLOSE_BRACKET(1),
            OPEN_C_BRACKET(1), PRINT_KEYWORD(2), INT_LITERAL(2, 1), SEMICOLON(2),
            CLOSE_C_BRACKET(3),
            ELSE_KEYWORD(3), OPEN_C_BRACKET(3),
            PRINT_KEYWORD(4), INT_LITERAL(4, 2), SEMICOLON(4),
            CLOSE_C_BRACKET(5),
        ]
        program = Parser(tokens).parse()
        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, IF_STATEMENT)
        assert stmt.false_body is not None

    def test_if_else_true_body(self):
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1), INT_LITERAL(1, 1), CLOSE_BRACKET(1),
            OPEN_C_BRACKET(1), PRINT_KEYWORD(2), INT_LITERAL(2, 10), SEMICOLON(2),
            CLOSE_C_BRACKET(3),
            ELSE_KEYWORD(3), OPEN_C_BRACKET(3),
            PRINT_KEYWORD(4), INT_LITERAL(4, 20), SEMICOLON(4),
            CLOSE_C_BRACKET(5),
        ]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        # true body has: OPEN_C, PRINT(10), CLOSE_C
        print_stmts = [s for s in stmt.true_body if isinstance(s, PRINT_STATEMENT)]
        assert len(print_stmts) == 1
        assert print_stmts[0].expr.val == 10

    def test_if_else_false_body(self):
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1), INT_LITERAL(1, 0), CLOSE_BRACKET(1),
            OPEN_C_BRACKET(1), PRINT_KEYWORD(2), INT_LITERAL(2, 10), SEMICOLON(2),
            CLOSE_C_BRACKET(3),
            ELSE_KEYWORD(3), OPEN_C_BRACKET(3),
            PRINT_KEYWORD(4), INT_LITERAL(4, 20), SEMICOLON(4),
            CLOSE_C_BRACKET(5),
        ]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        print_stmts = [s for s in stmt.false_body if isinstance(s, PRINT_STATEMENT)]
        assert len(print_stmts) == 1
        assert print_stmts[0].expr.val == 20

    def test_if_else_both_empty(self):
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1), INT_LITERAL(1, 1), CLOSE_BRACKET(1),
            OPEN_C_BRACKET(1), CLOSE_C_BRACKET(1),
            ELSE_KEYWORD(1), OPEN_C_BRACKET(1), CLOSE_C_BRACKET(1),
        ]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert isinstance(stmt, IF_STATEMENT)
        assert stmt.false_body is not None

    def test_if_else_multiple_statements_in_bodies(self):
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1), INT_LITERAL(1, 1), CLOSE_BRACKET(1),
            OPEN_C_BRACKET(1),
            PRINT_KEYWORD(2), INT_LITERAL(2, 1), SEMICOLON(2),
            PRINT_KEYWORD(3), INT_LITERAL(3, 2), SEMICOLON(3),
            CLOSE_C_BRACKET(4),
            ELSE_KEYWORD(4), OPEN_C_BRACKET(4),
            PRINT_KEYWORD(5), INT_LITERAL(5, 3), SEMICOLON(5),
            PRINT_KEYWORD(6), INT_LITERAL(6, 4), SEMICOLON(6),
            CLOSE_C_BRACKET(7),
        ]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        true_prints = [s for s in stmt.true_body if isinstance(s, PRINT_STATEMENT)]
        false_prints = [s for s in stmt.false_body if isinstance(s, PRINT_STATEMENT)]
        assert len(true_prints) == 2
        assert len(false_prints) == 2

    def test_else_missing_open_brace(self):
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1), INT_LITERAL(1, 1), CLOSE_BRACKET(1),
            OPEN_C_BRACKET(1), CLOSE_C_BRACKET(1),
            ELSE_KEYWORD(1), PRINT_KEYWORD(1), INT_LITERAL(1, 1), SEMICOLON(1),
        ]
        with pytest.raises(ValueError, match="expected"):
            Parser(tokens).parse()


class TestParserNestedIf:
    def test_nested_if_in_true_body(self):
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1), INT_LITERAL(1, 1), CLOSE_BRACKET(1),
            OPEN_C_BRACKET(1),
            IF_KEYWORD(2), OPEN_BRACKET(2), INT_LITERAL(2, 1), CLOSE_BRACKET(2),
            OPEN_C_BRACKET(2), PRINT_KEYWORD(3), INT_LITERAL(3, 42), SEMICOLON(3),
            CLOSE_C_BRACKET(4),
            CLOSE_C_BRACKET(5),
        ]
        program = Parser(tokens).parse()
        outer = program.statements[0]
        assert isinstance(outer, IF_STATEMENT)
        inner_ifs = [s for s in outer.true_body if isinstance(s, IF_STATEMENT)]
        assert len(inner_ifs) == 1
        assert inner_ifs[0].false_body is None

    def test_nested_if_else_in_true_body(self):
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1), INT_LITERAL(1, 1), CLOSE_BRACKET(1),
            OPEN_C_BRACKET(1),
            IF_KEYWORD(2), OPEN_BRACKET(2), INT_LITERAL(2, 0), CLOSE_BRACKET(2),
            OPEN_C_BRACKET(2), PRINT_KEYWORD(3), INT_LITERAL(3, 1), SEMICOLON(3),
            CLOSE_C_BRACKET(4),
            ELSE_KEYWORD(4), OPEN_C_BRACKET(4),
            PRINT_KEYWORD(5), INT_LITERAL(5, 2), SEMICOLON(5),
            CLOSE_C_BRACKET(6),
            CLOSE_C_BRACKET(7),
        ]
        program = Parser(tokens).parse()
        outer = program.statements[0]
        inner_ifs = [s for s in outer.true_body if isinstance(s, IF_STATEMENT)]
        assert len(inner_ifs) == 1
        assert inner_ifs[0].false_body is not None

    def test_nested_if_in_else_body(self):
        tokens = [
            IF_KEYWORD(1), OPEN_BRACKET(1), INT_LITERAL(1, 0), CLOSE_BRACKET(1),
            OPEN_C_BRACKET(1), PRINT_KEYWORD(2), INT_LITERAL(2, 1), SEMICOLON(2),
            CLOSE_C_BRACKET(3),
            ELSE_KEYWORD(3), OPEN_C_BRACKET(3),
            IF_KEYWORD(4), OPEN_BRACKET(4), INT_LITERAL(4, 1), CLOSE_BRACKET(4),
            OPEN_C_BRACKET(4), PRINT_KEYWORD(5), INT_LITERAL(5, 2), SEMICOLON(5),
            CLOSE_C_BRACKET(6),
            CLOSE_C_BRACKET(7),
        ]
        program = Parser(tokens).parse()
        outer = program.statements[0]
        inner_ifs = [s for s in outer.false_body if isinstance(s, IF_STATEMENT)]
        assert len(inner_ifs) == 1


class TestParserIfIntegration:
    def test_full_pipeline_simple_if(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("if (1) { print 42; }").tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 1
        assert isinstance(program.statements[0], IF_STATEMENT)
        assert program.statements[0].false_body is None

    def test_full_pipeline_if_else(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("if (0) { print 1; } else { print 2; }").tokenize()
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert isinstance(stmt, IF_STATEMENT)
        assert stmt.false_body is not None

    def test_full_pipeline_if_with_var_condition(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("int64 x = 1;\nif (x) { print 42; }").tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 2
        assert isinstance(program.statements[0], INT64_STATEMENT)
        assert isinstance(program.statements[1], IF_STATEMENT)
        assert isinstance(program.statements[1].expr, IDENTIFIER_EXPRESSION)

    def test_full_pipeline_if_with_expr_condition(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("if (1 + 2) { print 1; }").tokenize()
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert isinstance(stmt.expr, BINARY_EXPRESSION)

    def test_full_pipeline_nested_if_else(self):
        from tokenizer.tokenizer import Tokenizer
        src = "if (1) { if (0) { print 1; } else { print 2; } } else { print 3; }"
        tokens = Tokenizer(src).tokenize()
        program = Parser(tokens).parse()
        outer = program.statements[0]
        assert isinstance(outer, IF_STATEMENT)
        assert outer.false_body is not None
        inner_ifs = [s for s in outer.true_body if isinstance(s, IF_STATEMENT)]
        assert len(inner_ifs) == 1
        assert inner_ifs[0].false_body is not None

    def test_full_pipeline_if_with_vars_and_assign(self):
        from tokenizer.tokenizer import Tokenizer
        src = "int64 x = 1;\nif (x) {\n  int64 y = 10;\n  print y;\n}"
        tokens = Tokenizer(src).tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 2
        assert isinstance(program.statements[1], IF_STATEMENT)

    def test_full_pipeline_multiple_ifs(self):
        from tokenizer.tokenizer import Tokenizer
        src = "if (1) { print 1; }\nif (0) { print 2; }"
        tokens = Tokenizer(src).tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 2
        assert isinstance(program.statements[0], IF_STATEMENT)
        assert isinstance(program.statements[1], IF_STATEMENT)

    def test_full_pipeline_if_followed_by_statements(self):
        from tokenizer.tokenizer import Tokenizer
        src = "if (1) { print 1; }\nprint 99;\nexit 0;"
        tokens = Tokenizer(src).tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 3
        assert isinstance(program.statements[0], IF_STATEMENT)
        assert isinstance(program.statements[1], PRINT_STATEMENT)
        assert isinstance(program.statements[2], EXIT_STATEMENT)
