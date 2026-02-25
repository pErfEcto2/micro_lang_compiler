import pytest
from parser.parser import Parser
from parser.program import PROGRAM
from parser.statements import EXIT_STATEMENT, LET_STATEMENT
from parser.expressions import BINARY_EXPRESSION, IDENTIFIER_EXPRESSION, INT_EXPRESSION, STR_EXPRESSION
from tokenizer.keywords import ASSIGN_KEYWORD, EXIT_KEYWORD, LET_KEYWORD, MINUS_KEYWORD, MULTIPLY_KEYWORD, PLUS_KEYWORD, SEMICOLON
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
    def test_unexpected_token_identifier(self):
        tokens = [IDENTIFIER(1, "foo")]
        with pytest.raises(ValueError, match="unexpected token"):
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
        tokens = [IDENTIFIER(7, "badtoken")]
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

    def test_full_pipeline_identifier_fails(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("foo;").tokenize()
        with pytest.raises(ValueError, match="unexpected token"):
            Parser(tokens).parse()

    def test_full_pipeline_arithmetic(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("exit 1 + 2;").tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 1
        expr = program.statements[0].return_code
        assert isinstance(expr, BINARY_EXPRESSION)

    def test_full_pipeline_let_statement(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("let x = 5;").tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 1
        assert isinstance(program.statements[0], LET_STATEMENT)

    def test_full_pipeline_let_and_exit(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("let x = 5;\nexit x;").tokenize()
        program = Parser(tokens).parse()
        assert len(program.statements) == 2
        assert isinstance(program.statements[0], LET_STATEMENT)
        assert isinstance(program.statements[1], EXIT_STATEMENT)

    def test_full_pipeline_subtraction(self):
        from tokenizer.tokenizer import Tokenizer
        tokens = Tokenizer("exit 10 - 3;").tokenize()
        program = Parser(tokens).parse()
        expr = program.statements[0].return_code
        assert isinstance(expr, BINARY_EXPRESSION)


class TestParserLetStatement:
    def test_simple_let(self):
        tokens = [
            LET_KEYWORD(1), IDENTIFIER(1, "x"), ASSIGN_KEYWORD(1),
            INT_LITERAL(1, 5), SEMICOLON(1),
        ]
        program = Parser(tokens).parse()
        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, LET_STATEMENT)
        assert stmt.identifier.name == "x"
        assert isinstance(stmt.expr, INT_EXPRESSION)
        assert stmt.expr.val == 5

    def test_let_with_expression(self):
        tokens = [
            LET_KEYWORD(1), IDENTIFIER(1, "y"), ASSIGN_KEYWORD(1),
            INT_LITERAL(1, 1), PLUS_KEYWORD(1), INT_LITERAL(1, 2), SEMICOLON(1),
        ]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert isinstance(stmt, LET_STATEMENT)
        assert isinstance(stmt.expr, BINARY_EXPRESSION)

    def test_let_missing_identifier(self):
        tokens = [LET_KEYWORD(1), INT_LITERAL(1, 5), ASSIGN_KEYWORD(1), INT_LITERAL(1, 5), SEMICOLON(1)]
        with pytest.raises(ValueError, match="expected"):
            Parser(tokens).parse()

    def test_let_missing_assign(self):
        tokens = [LET_KEYWORD(1), IDENTIFIER(1, "x"), INT_LITERAL(1, 5), SEMICOLON(1)]
        with pytest.raises(ValueError, match="expected"):
            Parser(tokens).parse()

    def test_let_missing_semicolon(self):
        tokens = [LET_KEYWORD(1), IDENTIFIER(1, "x"), ASSIGN_KEYWORD(1), INT_LITERAL(1, 5)]
        with pytest.raises(ValueError, match="expected"):
            Parser(tokens).parse()

    def test_let_repr(self):
        stmt = LET_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5))
        assert "LET_STATEMENT" in repr(stmt)
        assert "x" in repr(stmt)

    def test_let_preserves_line_number(self):
        tokens = [
            LET_KEYWORD(3), IDENTIFIER(3, "z"), ASSIGN_KEYWORD(3),
            INT_LITERAL(3, 10), SEMICOLON(3),
        ]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert stmt.line_number == 3


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
