import pytest
from parser.parser import Parser
from parser.program import PROGRAM
from parser.statements import EXIT_STATEMENT
from parser.expressions import INT_EXPRESSION, STR_EXPRESSION
from tokenizer.keywords import EXIT_KEYWORD, SEMICOLON
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

    def test_exit_with_str(self):
        tokens = [EXIT_KEYWORD(1), STR_LITERAL(1, "hello"), SEMICOLON(1)]
        program = Parser(tokens).parse()
        stmt = program.statements[0]
        assert isinstance(stmt, EXIT_STATEMENT)
        assert isinstance(stmt.return_code, STR_EXPRESSION)
        assert stmt.return_code.val == "hello"

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

    def test_unexpected_expression_identifier(self):
        tokens = [EXIT_KEYWORD(1), IDENTIFIER(1, "x"), SEMICOLON(1)]
        with pytest.raises(ValueError, match="unexpected expression"):
            Parser(tokens).parse()

    def test_error_reports_line_number(self):
        tokens = [IDENTIFIER(7, "badtoken")]
        with pytest.raises(ValueError, match="line 7"):
            Parser(tokens).parse()

    def test_expression_error_reports_line_number(self):
        tokens = [EXIT_KEYWORD(3), IDENTIFIER(3, "x"), SEMICOLON(3)]
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

    def test_str_expression_value(self):
        tokens = [EXIT_KEYWORD(1), STR_LITERAL(1, "world"), SEMICOLON(1)]
        program = Parser(tokens).parse()
        expr = program.statements[0].return_code
        assert isinstance(expr, STR_EXPRESSION)
        assert expr.val == "world"
        assert expr.line_number == 1

    def test_str_expression_empty(self):
        tokens = [EXIT_KEYWORD(1), STR_LITERAL(1, ""), SEMICOLON(1)]
        program = Parser(tokens).parse()
        expr = program.statements[0].return_code
        assert isinstance(expr, STR_EXPRESSION)
        assert expr.val == ""

    def test_int_expression_repr(self):
        expr = INT_EXPRESSION(1, 42)
        assert repr(expr) == "INT_EXPRESSION(42)"

    def test_str_expression_repr(self):
        expr = STR_EXPRESSION(1, "hello")
        assert repr(expr) == "STR_EXPRESSION(hello)"

    def test_str_expression_str(self):
        expr = STR_EXPRESSION(1, "world")
        assert str(expr) == "STR_EXPRESSION(world)"


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
