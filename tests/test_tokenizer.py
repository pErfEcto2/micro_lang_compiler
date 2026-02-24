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

    def test_invalid_digit_raises(self):
        with pytest.raises(ValueError, match="invalid digit"):
            Tokenizer("123abc").tokenize()

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

    def test_invalid_number_reports_line(self):
        with pytest.raises(ValueError, match="line 1"):
            Tokenizer("12x").tokenize()


class TestTokenizerRepr:
    def test_exit_keyword_repr(self):
        tokens = Tokenizer("exit").tokenize()
        assert repr(tokens[0]) == "EXIT_KEYWORD"

    def test_semicolon_repr(self):
        tokens = Tokenizer(";").tokenize()
        assert repr(tokens[0]) == "SEMICOLON"

    def test_int_literal_repr(self):
        tokens = Tokenizer("42").tokenize()
        assert repr(tokens[0]) == "INT_LITERAL(42)"

    def test_identifier_repr(self):
        tokens = Tokenizer("foo").tokenize()
        assert repr(tokens[0]) == "IDENTIFIER(foo)"
