import pytest
from tokenizer.tokenizer import Tokenizer
from tokenizer.keywords import EXIT_KEYWORD, SEMICOLON
from tokenizer.literals import INT_LITERAL
from tokenizer.tokens import IDENTIFIER


class TestTokenizerBasic:
    def test_empty_input(self):
        tokens = Tokenizer("").tokenize()
        assert tokens == []

    def test_whitespace_only(self):
        tokens = Tokenizer("   \t\t  \n\n  ").tokenize()
        assert tokens == []

    def test_semicolon(self):
        tokens = Tokenizer(";").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], SEMICOLON)

    def test_multiple_semicolons(self):
        tokens = Tokenizer(";;;").tokenize()
        assert len(tokens) == 3
        assert all(isinstance(t, SEMICOLON) for t in tokens)


class TestTokenizerKeywords:
    def test_exit_keyword(self):
        tokens = Tokenizer("exit").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], EXIT_KEYWORD)

    def test_exit_with_semicolon(self):
        tokens = Tokenizer("exit;").tokenize()
        assert len(tokens) == 2
        assert isinstance(tokens[0], EXIT_KEYWORD)
        assert isinstance(tokens[1], SEMICOLON)

    def test_exit_with_spaces(self):
        tokens = Tokenizer("  exit  ").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], EXIT_KEYWORD)


class TestTokenizerLiterals:
    def test_int_literal(self):
        tokens = Tokenizer("42").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], INT_LITERAL)
        assert tokens[0].val == 42

    def test_int_literal_zero(self):
        tokens = Tokenizer("0").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], INT_LITERAL)
        assert tokens[0].val == 0

    def test_large_int_literal(self):
        tokens = Tokenizer("999999").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], INT_LITERAL)
        assert tokens[0].val == 999999

    def test_number_followed_by_alpha(self):
        tokens = Tokenizer("123abc").tokenize()
        assert len(tokens) == 2
        assert isinstance(tokens[0], INT_LITERAL)
        assert tokens[0].val == 123
        assert isinstance(tokens[1], IDENTIFIER)
        assert tokens[1].val == "abc"

    def test_identifier(self):
        tokens = Tokenizer("foo").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], IDENTIFIER)
        assert tokens[0].val == "foo"

    def test_identifier_with_digits(self):
        tokens = Tokenizer("var1").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], IDENTIFIER)
        assert tokens[0].val == "var1"


class TestTokenizerStatements:
    def test_exit_statement(self):
        tokens = Tokenizer("exit 69;").tokenize()
        assert len(tokens) == 3
        assert isinstance(tokens[0], EXIT_KEYWORD)
        assert isinstance(tokens[1], INT_LITERAL)
        assert tokens[1].val == 69
        assert isinstance(tokens[2], SEMICOLON)

    def test_multiple_statements(self):
        tokens = Tokenizer("exit 69;\nexit 70;").tokenize()
        assert len(tokens) == 6
        assert isinstance(tokens[0], EXIT_KEYWORD)
        assert isinstance(tokens[1], INT_LITERAL)
        assert tokens[1].val == 69
        assert isinstance(tokens[2], SEMICOLON)
        assert isinstance(tokens[3], EXIT_KEYWORD)
        assert isinstance(tokens[4], INT_LITERAL)
        assert tokens[4].val == 70
        assert isinstance(tokens[5], SEMICOLON)

    def test_identifier_statement(self):
        tokens = Tokenizer("asotehu;").tokenize()
        assert len(tokens) == 2
        assert isinstance(tokens[0], IDENTIFIER)
        assert tokens[0].val == "asotehu"
        assert isinstance(tokens[1], SEMICOLON)

    def test_full_test_file(self):
        tokens = Tokenizer("exit 69;\nexit 70;\nasotehu;\n").tokenize()
        assert len(tokens) == 8
        assert isinstance(tokens[0], EXIT_KEYWORD)
        assert isinstance(tokens[1], INT_LITERAL)
        assert isinstance(tokens[2], SEMICOLON)
        assert isinstance(tokens[3], EXIT_KEYWORD)
        assert isinstance(tokens[4], INT_LITERAL)
        assert isinstance(tokens[5], SEMICOLON)
        assert isinstance(tokens[6], IDENTIFIER)
        assert isinstance(tokens[7], SEMICOLON)


class TestTokenizerLineNumbers:
    def test_first_line(self):
        tokens = Tokenizer("exit;").tokenize()
        assert tokens[0].line_number == 1

    def test_second_line(self):
        tokens = Tokenizer("\nexit;").tokenize()
        assert tokens[0].line_number == 2

    def test_multiple_lines(self):
        tokens = Tokenizer("exit;\nexit;\nexit;").tokenize()
        assert tokens[0].line_number == 1
        assert tokens[2].line_number == 2
        assert tokens[4].line_number == 3


class TestTokenizerErrors:
    def test_unknown_character(self):
        with pytest.raises(ValueError, match="unknown character"):
            Tokenizer("@").tokenize()

    def test_unknown_character_reports_line(self):
        with pytest.raises(ValueError, match="line 2"):
            Tokenizer("\n@").tokenize()


class TestTokenizerOperators:
    def test_plus(self):
        from tokenizer.keywords import PLUS_KEYWORD
        tokens = Tokenizer("+").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], PLUS_KEYWORD)

    def test_multiply(self):
        from tokenizer.keywords import MULTIPLY_KEYWORD
        tokens = Tokenizer("*").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], MULTIPLY_KEYWORD)

    def test_assign(self):
        from tokenizer.keywords import ASSIGN_KEYWORD
        tokens = Tokenizer("=").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], ASSIGN_KEYWORD)

    def test_arithmetic_expression(self):
        from tokenizer.keywords import PLUS_KEYWORD, MULTIPLY_KEYWORD
        tokens = Tokenizer("1+2*3").tokenize()
        assert len(tokens) == 5
        assert isinstance(tokens[0], INT_LITERAL)
        assert isinstance(tokens[1], PLUS_KEYWORD)
        assert isinstance(tokens[2], INT_LITERAL)
        assert isinstance(tokens[3], MULTIPLY_KEYWORD)
        assert isinstance(tokens[4], INT_LITERAL)

    def test_arithmetic_with_spaces(self):
        from tokenizer.keywords import PLUS_KEYWORD
        tokens = Tokenizer("10 + 20").tokenize()
        assert len(tokens) == 3
        assert tokens[0].val == 10
        assert isinstance(tokens[1], PLUS_KEYWORD)
        assert tokens[2].val == 20

    def test_plus_repr(self):
        tokens = Tokenizer("+").tokenize()
        assert repr(tokens[0]) == "+"

    def test_multiply_repr(self):
        tokens = Tokenizer("*").tokenize()
        assert repr(tokens[0]) == "*"

    def test_assign_repr(self):
        tokens = Tokenizer("=").tokenize()
        assert repr(tokens[0]) == "="

    def test_minus(self):
        from tokenizer.keywords import MINUS_KEYWORD
        tokens = Tokenizer("-").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], MINUS_KEYWORD)

    def test_minus_repr(self):
        tokens = Tokenizer("-").tokenize()
        assert repr(tokens[0]) == "-"

    def test_int_division(self):
        from tokenizer.keywords import INT_DIVISION_KEYWORD
        tokens = Tokenizer("//").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], INT_DIVISION_KEYWORD)

    def test_int_division_repr(self):
        tokens = Tokenizer("//").tokenize()
        assert repr(tokens[0]) == "//"

    def test_modulo(self):
        from tokenizer.keywords import MODULO_KEYWORD
        tokens = Tokenizer("%").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], MODULO_KEYWORD)

    def test_modulo_repr(self):
        tokens = Tokenizer("%").tokenize()
        assert repr(tokens[0]) == "%"

    def test_subtraction_expression(self):
        from tokenizer.keywords import MINUS_KEYWORD
        tokens = Tokenizer("10 - 3").tokenize()
        assert len(tokens) == 3
        assert tokens[0].val == 10
        assert isinstance(tokens[1], MINUS_KEYWORD)
        assert tokens[2].val == 3

    def test_int_division_expression(self):
        from tokenizer.keywords import INT_DIVISION_KEYWORD
        tokens = Tokenizer("10 // 3").tokenize()
        assert len(tokens) == 3
        assert tokens[0].val == 10
        assert isinstance(tokens[1], INT_DIVISION_KEYWORD)
        assert tokens[2].val == 3

    def test_modulo_expression(self):
        from tokenizer.keywords import MODULO_KEYWORD
        tokens = Tokenizer("10 % 3").tokenize()
        assert len(tokens) == 3
        assert tokens[0].val == 10
        assert isinstance(tokens[1], MODULO_KEYWORD)
        assert tokens[2].val == 3


class TestTokenizerLetStatement:
    def test_let_keyword(self):
        from tokenizer.keywords import LET_KEYWORD
        tokens = Tokenizer("let").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], LET_KEYWORD)

    def test_let_keyword_repr(self):
        tokens = Tokenizer("let").tokenize()
        assert repr(tokens[0]) == "let"

    def test_let_statement(self):
        from tokenizer.keywords import ASSIGN_KEYWORD, LET_KEYWORD
        tokens = Tokenizer("let x = 5;").tokenize()
        assert len(tokens) == 5
        assert isinstance(tokens[0], LET_KEYWORD)
        assert isinstance(tokens[1], IDENTIFIER)
        assert tokens[1].val == "x"
        assert isinstance(tokens[2], ASSIGN_KEYWORD)
        assert isinstance(tokens[3], INT_LITERAL)
        assert tokens[3].val == 5
        assert isinstance(tokens[4], SEMICOLON)

    def test_let_with_expression(self):
        from tokenizer.keywords import LET_KEYWORD, ASSIGN_KEYWORD, PLUS_KEYWORD
        tokens = Tokenizer("let y = 1 + 2;").tokenize()
        assert len(tokens) == 7
        assert isinstance(tokens[0], LET_KEYWORD)
        assert isinstance(tokens[1], IDENTIFIER)
        assert isinstance(tokens[2], ASSIGN_KEYWORD)
        assert isinstance(tokens[3], INT_LITERAL)
        assert isinstance(tokens[4], PLUS_KEYWORD)
        assert isinstance(tokens[5], INT_LITERAL)
        assert isinstance(tokens[6], SEMICOLON)


class TestTokenizerPrintKeyword:
    def test_print_keyword(self):
        from tokenizer.keywords import PRINT_KEYWORD
        tokens = Tokenizer("print").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], PRINT_KEYWORD)

    def test_print_keyword_repr(self):
        tokens = Tokenizer("print").tokenize()
        assert repr(tokens[0]) == "print"

    def test_print_statement_tokens(self):
        from tokenizer.keywords import PRINT_KEYWORD
        tokens = Tokenizer("print 42;").tokenize()
        assert len(tokens) == 3
        assert isinstance(tokens[0], PRINT_KEYWORD)
        assert isinstance(tokens[1], INT_LITERAL)
        assert tokens[1].val == 42
        assert isinstance(tokens[2], SEMICOLON)

    def test_print_with_expression(self):
        from tokenizer.keywords import PRINT_KEYWORD, PLUS_KEYWORD
        tokens = Tokenizer("print 1 + 2;").tokenize()
        assert len(tokens) == 5
        assert isinstance(tokens[0], PRINT_KEYWORD)
        assert isinstance(tokens[1], INT_LITERAL)
        assert isinstance(tokens[2], PLUS_KEYWORD)
        assert isinstance(tokens[3], INT_LITERAL)
        assert isinstance(tokens[4], SEMICOLON)


class TestTokenizerRepr:
    def test_exit_keyword_repr(self):
        tokens = Tokenizer("exit").tokenize()
        assert repr(tokens[0]) == "exit"

    def test_semicolon_repr(self):
        tokens = Tokenizer(";").tokenize()
        assert repr(tokens[0]) == ";"

    def test_int_literal_repr(self):
        tokens = Tokenizer("42").tokenize()
        assert repr(tokens[0]) == "42"

    def test_identifier_repr(self):
        tokens = Tokenizer("foo").tokenize()
        assert repr(tokens[0]) == "foo"

    def test_str_literal_repr(self):
        from tokenizer.literals import STR_LITERAL
        lit = STR_LITERAL(1, "hello")
        assert repr(lit) == "hello"

    def test_str_literal_str(self):
        from tokenizer.literals import STR_LITERAL
        lit = STR_LITERAL(1, "world")
        assert str(lit) == "world"
