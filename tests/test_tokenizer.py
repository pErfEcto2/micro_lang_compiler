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
        with pytest.raises(ValueError, match="invalid syntax in line 1"):
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


class TestTokenizerInt64Statement:
    def test_int64_keyword(self):
        from tokenizer.keywords import INT64_KEYWORD
        tokens = Tokenizer("int64").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], INT64_KEYWORD)

    def test_int64_keyword_repr(self):
        tokens = Tokenizer("int64").tokenize()
        assert repr(tokens[0]) == "int64"

    def test_int64_statement(self):
        from tokenizer.keywords import ASSIGN_KEYWORD, INT64_KEYWORD
        tokens = Tokenizer("int64 x = 5;").tokenize()
        assert len(tokens) == 5
        assert isinstance(tokens[0], INT64_KEYWORD)
        assert isinstance(tokens[1], IDENTIFIER)
        assert tokens[1].val == "x"
        assert isinstance(tokens[2], ASSIGN_KEYWORD)
        assert isinstance(tokens[3], INT_LITERAL)
        assert tokens[3].val == 5
        assert isinstance(tokens[4], SEMICOLON)

    def test_int64_with_expression(self):
        from tokenizer.keywords import INT64_KEYWORD, ASSIGN_KEYWORD, PLUS_KEYWORD
        tokens = Tokenizer("int64 y = 1 + 2;").tokenize()
        assert len(tokens) == 7
        assert isinstance(tokens[0], INT64_KEYWORD)
        assert isinstance(tokens[1], IDENTIFIER)
        assert isinstance(tokens[2], ASSIGN_KEYWORD)
        assert isinstance(tokens[3], INT_LITERAL)
        assert isinstance(tokens[4], PLUS_KEYWORD)
        assert isinstance(tokens[5], INT_LITERAL)
        assert isinstance(tokens[6], SEMICOLON)


class TestTokenizerConstKeyword:
    def test_const_keyword(self):
        from tokenizer.keywords import CONST_KEYWORD
        tokens = Tokenizer("const").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], CONST_KEYWORD)

    def test_const_keyword_repr(self):
        tokens = Tokenizer("const").tokenize()
        assert repr(tokens[0]) == "const"

    def test_const_int64_statement(self):
        from tokenizer.keywords import CONST_KEYWORD, INT64_KEYWORD, ASSIGN_KEYWORD
        tokens = Tokenizer("const int64 x = 5;").tokenize()
        assert len(tokens) == 6
        assert isinstance(tokens[0], CONST_KEYWORD)
        assert isinstance(tokens[1], INT64_KEYWORD)
        assert isinstance(tokens[2], IDENTIFIER)
        assert tokens[2].val == "x"
        assert isinstance(tokens[3], ASSIGN_KEYWORD)
        assert isinstance(tokens[4], INT_LITERAL)
        assert tokens[4].val == 5
        assert isinstance(tokens[5], SEMICOLON)


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


class TestTokenizerCurlyBrackets:
    def test_open_bracket(self):
        from tokenizer.keywords import OPEN_C_BRACKET
        tokens = Tokenizer("{}").tokenize()
        assert isinstance(tokens[0], OPEN_C_BRACKET)

    def test_close_bracket(self):
        from tokenizer.keywords import CLOSE_C_BRACKET
        tokens = Tokenizer("{}").tokenize()
        assert len(tokens) == 2
        assert isinstance(tokens[1], CLOSE_C_BRACKET)

    def test_open_bracket_repr(self):
        tokens = Tokenizer("{}").tokenize()
        assert repr(tokens[0]) == "{"

    def test_close_bracket_repr(self):
        tokens = Tokenizer("{}").tokenize()
        assert repr(tokens[1]) == "}"

    def test_nested_brackets(self):
        from tokenizer.keywords import OPEN_C_BRACKET, CLOSE_C_BRACKET
        tokens = Tokenizer("{ { } }").tokenize()
        assert len(tokens) == 4
        assert isinstance(tokens[0], OPEN_C_BRACKET)
        assert isinstance(tokens[1], OPEN_C_BRACKET)
        assert isinstance(tokens[2], CLOSE_C_BRACKET)
        assert isinstance(tokens[3], CLOSE_C_BRACKET)

    def test_brackets_with_statements(self):
        from tokenizer.keywords import OPEN_C_BRACKET, CLOSE_C_BRACKET, INT64_KEYWORD, ASSIGN_KEYWORD
        tokens = Tokenizer("{ int64 x = 5; }").tokenize()
        assert isinstance(tokens[0], OPEN_C_BRACKET)
        assert isinstance(tokens[1], INT64_KEYWORD)
        assert isinstance(tokens[-1], CLOSE_C_BRACKET)

    def test_unmatched_open_bracket_raises(self):
        with pytest.raises(ValueError, match="unmatched"):
            Tokenizer("{").tokenize()

    def test_unmatched_close_bracket_raises(self):
        with pytest.raises(ValueError, match="unmatched"):
            Tokenizer("}").tokenize()

    def test_bracket_line_numbers(self):
        tokens = Tokenizer("{\n}").tokenize()
        assert tokens[0].line_number == 1
        assert tokens[1].line_number == 2


class TestTokenizerParentheses:
    def test_open_bracket(self):
        from tokenizer.keywords import OPEN_BRACKET
        tokens = Tokenizer("(").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], OPEN_BRACKET)

    def test_close_bracket(self):
        from tokenizer.keywords import CLOSE_BRACKET
        tokens = Tokenizer("()").tokenize()
        assert len(tokens) == 2
        assert isinstance(tokens[1], CLOSE_BRACKET)

    def test_open_bracket_repr(self):
        tokens = Tokenizer("()").tokenize()
        assert repr(tokens[0]) == "("

    def test_close_bracket_repr(self):
        tokens = Tokenizer("()").tokenize()
        assert repr(tokens[1]) == ")"

    def test_parentheses_in_expression(self):
        from tokenizer.keywords import OPEN_BRACKET, CLOSE_BRACKET
        tokens = Tokenizer("(1)").tokenize()
        assert len(tokens) == 3
        assert isinstance(tokens[0], OPEN_BRACKET)
        assert isinstance(tokens[1], INT_LITERAL)
        assert isinstance(tokens[2], CLOSE_BRACKET)

    def test_parentheses_stop_word_parsing(self):
        from tokenizer.keywords import OPEN_BRACKET
        tokens = Tokenizer("if(").tokenize()
        assert len(tokens) == 2
        assert tokens[0].val if hasattr(tokens[0], 'val') else str(tokens[0]) == "if"
        assert isinstance(tokens[1], OPEN_BRACKET)

    def test_parentheses_stop_number_parsing(self):
        from tokenizer.keywords import CLOSE_BRACKET
        tokens = Tokenizer("42)").tokenize()
        assert len(tokens) == 2
        assert isinstance(tokens[0], INT_LITERAL)
        assert tokens[0].val == 42
        assert isinstance(tokens[1], CLOSE_BRACKET)

    def test_parentheses_line_numbers(self):
        tokens = Tokenizer("(\n)").tokenize()
        assert tokens[0].line_number == 1
        assert tokens[1].line_number == 2


class TestTokenizerIfElseKeywords:
    def test_if_keyword(self):
        from tokenizer.keywords import IF_KEYWORD
        tokens = Tokenizer("if").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], IF_KEYWORD)

    def test_if_keyword_repr(self):
        tokens = Tokenizer("if").tokenize()
        assert repr(tokens[0]) == "if"

    def test_else_keyword(self):
        from tokenizer.keywords import ELSE_KEYWORD
        tokens = Tokenizer("else").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], ELSE_KEYWORD)

    def test_else_keyword_repr(self):
        tokens = Tokenizer("else").tokenize()
        assert repr(tokens[0]) == "else"

    def test_if_statement_tokens(self):
        from tokenizer.keywords import IF_KEYWORD, OPEN_BRACKET, CLOSE_BRACKET, OPEN_C_BRACKET, CLOSE_C_BRACKET, PRINT_KEYWORD
        tokens = Tokenizer("if (1) { print 1; }").tokenize()
        assert isinstance(tokens[0], IF_KEYWORD)
        assert isinstance(tokens[1], OPEN_BRACKET)
        assert isinstance(tokens[2], INT_LITERAL)
        assert isinstance(tokens[3], CLOSE_BRACKET)
        assert isinstance(tokens[4], OPEN_C_BRACKET)
        assert isinstance(tokens[5], PRINT_KEYWORD)
        assert isinstance(tokens[6], INT_LITERAL)
        assert isinstance(tokens[7], SEMICOLON)
        assert isinstance(tokens[8], CLOSE_C_BRACKET)

    def test_if_else_tokens(self):
        from tokenizer.keywords import IF_KEYWORD, ELSE_KEYWORD, OPEN_BRACKET, CLOSE_BRACKET, OPEN_C_BRACKET, CLOSE_C_BRACKET
        tokens = Tokenizer("if (1) { } else { }").tokenize()
        assert isinstance(tokens[0], IF_KEYWORD)
        assert isinstance(tokens[1], OPEN_BRACKET)
        assert isinstance(tokens[2], INT_LITERAL)
        assert isinstance(tokens[3], CLOSE_BRACKET)
        assert isinstance(tokens[4], OPEN_C_BRACKET)
        assert isinstance(tokens[5], CLOSE_C_BRACKET)
        assert isinstance(tokens[6], ELSE_KEYWORD)
        assert isinstance(tokens[7], OPEN_C_BRACKET)
        assert isinstance(tokens[8], CLOSE_C_BRACKET)

    def test_if_not_identifier(self):
        from tokenizer.keywords import IF_KEYWORD
        tokens = Tokenizer("if").tokenize()
        assert not isinstance(tokens[0], IDENTIFIER)
        assert isinstance(tokens[0], IF_KEYWORD)

    def test_else_not_identifier(self):
        from tokenizer.keywords import ELSE_KEYWORD
        tokens = Tokenizer("else").tokenize()
        assert not isinstance(tokens[0], IDENTIFIER)
        assert isinstance(tokens[0], ELSE_KEYWORD)

    def test_ifdef_is_identifier(self):
        tokens = Tokenizer("ifdef").tokenize()
        assert isinstance(tokens[0], IDENTIFIER)
        assert tokens[0].val == "ifdef"

    def test_if_with_no_space_before_paren(self):
        from tokenizer.keywords import IF_KEYWORD, OPEN_BRACKET
        tokens = Tokenizer("if(1){}").tokenize()
        assert isinstance(tokens[0], IF_KEYWORD)
        assert isinstance(tokens[1], OPEN_BRACKET)


class TestTokenizerSlashError:
    def test_lone_slash_raises(self):
        with pytest.raises(ValueError, match="invalid syntax"):
            Tokenizer("/").tokenize()

    def test_slash_followed_by_non_slash_raises(self):
        with pytest.raises(ValueError, match="invalid syntax"):
            Tokenizer("/3").tokenize()


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


class TestTokenizerWhileKeyword:
    def test_while_keyword(self):
        from tokenizer.keywords import WHILE_KEYWORD
        tokens = Tokenizer("while").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], WHILE_KEYWORD)

    def test_while_keyword_repr(self):
        tokens = Tokenizer("while").tokenize()
        assert repr(tokens[0]) == "while"

    def test_while_not_identifier(self):
        from tokenizer.keywords import WHILE_KEYWORD
        tokens = Tokenizer("while").tokenize()
        assert not isinstance(tokens[0], IDENTIFIER)
        assert isinstance(tokens[0], WHILE_KEYWORD)

    def test_whilevar_is_identifier(self):
        tokens = Tokenizer("whilevar").tokenize()
        assert isinstance(tokens[0], IDENTIFIER)
        assert tokens[0].val == "whilevar"

    def test_while_with_no_space_before_paren(self):
        from tokenizer.keywords import WHILE_KEYWORD, OPEN_BRACKET
        tokens = Tokenizer("while(1){}").tokenize()
        assert isinstance(tokens[0], WHILE_KEYWORD)
        assert isinstance(tokens[1], OPEN_BRACKET)

    def test_while_statement_tokens(self):
        from tokenizer.keywords import WHILE_KEYWORD, OPEN_BRACKET, CLOSE_BRACKET, LESS_KEYWORD, OPEN_C_BRACKET, CLOSE_C_BRACKET, PRINT_KEYWORD
        tokens = Tokenizer("while (i < 10) { print i; }").tokenize()
        assert isinstance(tokens[0], WHILE_KEYWORD)
        assert isinstance(tokens[1], OPEN_BRACKET)
        assert isinstance(tokens[2], IDENTIFIER)
        assert tokens[2].val == "i"
        assert isinstance(tokens[3], LESS_KEYWORD)
        assert isinstance(tokens[4], INT_LITERAL)
        assert tokens[4].val == 10
        assert isinstance(tokens[5], CLOSE_BRACKET)
        assert isinstance(tokens[6], OPEN_C_BRACKET)
        assert isinstance(tokens[7], PRINT_KEYWORD)
        assert isinstance(tokens[8], IDENTIFIER)
        assert tokens[8].val == "i"
        assert isinstance(tokens[9], SEMICOLON)
        assert isinstance(tokens[10], CLOSE_C_BRACKET)


class TestTokenizerComparisonOperators:
    def test_greater_than(self):
        from tokenizer.keywords import GREATER_KEYWORD
        tokens = Tokenizer(">").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], GREATER_KEYWORD)

    def test_less_than(self):
        from tokenizer.keywords import LESS_KEYWORD
        tokens = Tokenizer("<").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], LESS_KEYWORD)

    def test_greater_or_equals(self):
        from tokenizer.keywords import GREATER_OR_EQUALS_KEYWORD
        tokens = Tokenizer(">=").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], GREATER_OR_EQUALS_KEYWORD)

    def test_less_or_equals(self):
        from tokenizer.keywords import LESS_OR_EQUALS_KEYWORD
        tokens = Tokenizer("<=").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], LESS_OR_EQUALS_KEYWORD)

    def test_greater_repr(self):
        tokens = Tokenizer(">").tokenize()
        assert repr(tokens[0]) == ">"

    def test_less_repr(self):
        tokens = Tokenizer("<").tokenize()
        assert repr(tokens[0]) == "<"

    def test_greater_or_equals_repr(self):
        tokens = Tokenizer(">=").tokenize()
        assert repr(tokens[0]) == ">="

    def test_less_or_equals_repr(self):
        tokens = Tokenizer("<=").tokenize()
        assert repr(tokens[0]) == "<="

    def test_comparison_in_expression(self):
        from tokenizer.keywords import LESS_KEYWORD
        tokens = Tokenizer("x < 10").tokenize()
        assert len(tokens) == 3
        assert isinstance(tokens[0], IDENTIFIER)
        assert isinstance(tokens[1], LESS_KEYWORD)
        assert isinstance(tokens[2], INT_LITERAL)

    def test_comparison_no_spaces(self):
        from tokenizer.keywords import GREATER_KEYWORD
        tokens = Tokenizer("x>0").tokenize()
        assert len(tokens) == 3
        assert isinstance(tokens[0], IDENTIFIER)
        assert tokens[0].val == "x"
        assert isinstance(tokens[1], GREATER_KEYWORD)
        assert isinstance(tokens[2], INT_LITERAL)
        assert tokens[2].val == 0

    def test_equals(self):
        from tokenizer.keywords import EQUALS_KEYWORD
        tokens = Tokenizer("==").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], EQUALS_KEYWORD)

    def test_not_equals(self):
        from tokenizer.keywords import NOT_EQUALS_KEYWORD
        tokens = Tokenizer("!=").tokenize()
        assert len(tokens) == 1
        assert isinstance(tokens[0], NOT_EQUALS_KEYWORD)

    def test_equals_repr(self):
        tokens = Tokenizer("==").tokenize()
        assert repr(tokens[0]) == "=="

    def test_not_equals_repr(self):
        tokens = Tokenizer("!=").tokenize()
        assert repr(tokens[0]) == "!="

    def test_equals_in_expression(self):
        from tokenizer.keywords import EQUALS_KEYWORD
        tokens = Tokenizer("x == 5").tokenize()
        assert len(tokens) == 3
        assert isinstance(tokens[0], IDENTIFIER)
        assert isinstance(tokens[1], EQUALS_KEYWORD)
        assert isinstance(tokens[2], INT_LITERAL)

    def test_not_equals_in_expression(self):
        from tokenizer.keywords import NOT_EQUALS_KEYWORD
        tokens = Tokenizer("x != 5").tokenize()
        assert len(tokens) == 3
        assert isinstance(tokens[0], IDENTIFIER)
        assert isinstance(tokens[1], NOT_EQUALS_KEYWORD)
        assert isinstance(tokens[2], INT_LITERAL)

    def test_equals_no_spaces(self):
        from tokenizer.keywords import EQUALS_KEYWORD
        tokens = Tokenizer("x==0").tokenize()
        assert len(tokens) == 3
        assert isinstance(tokens[0], IDENTIFIER)
        assert tokens[0].val == "x"
        assert isinstance(tokens[1], EQUALS_KEYWORD)
        assert isinstance(tokens[2], INT_LITERAL)
        assert tokens[2].val == 0

    def test_not_equals_no_spaces(self):
        from tokenizer.keywords import NOT_EQUALS_KEYWORD
        tokens = Tokenizer("x!=0").tokenize()
        assert len(tokens) == 3
        assert isinstance(tokens[0], IDENTIFIER)
        assert tokens[0].val == "x"
        assert isinstance(tokens[1], NOT_EQUALS_KEYWORD)
        assert isinstance(tokens[2], INT_LITERAL)
        assert tokens[2].val == 0

    def test_lone_bang_raises(self):
        with pytest.raises(ValueError, match="invalid syntax"):
            Tokenizer("!").tokenize()


class TestTokenizerSingleLineComment:
    def test_comment_only(self):
        tokens = Tokenizer("# hello world").tokenize()
        assert tokens == []

    def test_comment_is_ignored(self):
        tokens = Tokenizer("exit 0;\n# this is a comment\nexit 1;").tokenize()
        assert len(tokens) == 6
        assert isinstance(tokens[0], EXIT_KEYWORD)
        assert isinstance(tokens[3], EXIT_KEYWORD)

    def test_comment_at_end_of_file(self):
        tokens = Tokenizer("exit 0;\n# trailing comment").tokenize()
        assert len(tokens) == 3
        assert isinstance(tokens[0], EXIT_KEYWORD)

    def test_comment_preserves_line_numbers(self):
        tokens = Tokenizer("# comment\nexit 0;").tokenize()
        assert tokens[0].line_number == 2

    def test_multiple_comments(self):
        tokens = Tokenizer("# first\n# second\nexit 0;").tokenize()
        assert len(tokens) == 3
        assert tokens[0].line_number == 3

    def test_comment_after_statement(self):
        tokens = Tokenizer("exit 0;\n# comment").tokenize()
        assert len(tokens) == 3

    def test_comment_does_not_affect_previous_line(self):
        tokens = Tokenizer("exit 0;\n# comment").tokenize()
        assert len(tokens) == 3
        assert isinstance(tokens[0], EXIT_KEYWORD)
        assert isinstance(tokens[1], INT_LITERAL)
        assert isinstance(tokens[2], SEMICOLON)

    def test_empty_comment(self):
        tokens = Tokenizer("#\nexit 0;").tokenize()
        assert len(tokens) == 3
        assert tokens[0].line_number == 2


class TestTokenizerMultiLineComment:
    def test_simple_multiline_comment(self):
        tokens = Tokenizer("/* hello */").tokenize()
        assert tokens == []

    def test_multiline_comment_is_ignored(self):
        tokens = Tokenizer("exit 0;\n/* comment */\nexit 1;").tokenize()
        assert len(tokens) == 6
        assert isinstance(tokens[0], EXIT_KEYWORD)
        assert isinstance(tokens[3], EXIT_KEYWORD)

    def test_multiline_comment_spanning_lines(self):
        tokens = Tokenizer("exit 0;\n/* line1\nline2\nline3 */\nexit 1;").tokenize()
        assert len(tokens) == 6

    def test_multiline_comment_preserves_line_numbers(self):
        tokens = Tokenizer("/* comment\nspanning\nlines */\nexit 0;").tokenize()
        assert tokens[0].line_number == 4

    def test_multiline_comment_between_tokens(self):
        tokens = Tokenizer("exit /* skip */ 0;").tokenize()
        assert len(tokens) == 3
        assert isinstance(tokens[0], EXIT_KEYWORD)
        assert isinstance(tokens[1], INT_LITERAL)
        assert tokens[1].val == 0
        assert isinstance(tokens[2], SEMICOLON)

    def test_unterminated_multiline_comment_raises(self):
        with pytest.raises(ValueError, match="never closed"):
            Tokenizer("/* unterminated").tokenize()

    def test_unterminated_multiline_comment_reports_line(self):
        with pytest.raises(ValueError, match="line 1"):
            Tokenizer("/* unterminated").tokenize()

    def test_unterminated_multiline_comment_on_later_line(self):
        with pytest.raises(ValueError, match="line 2"):
            Tokenizer("exit 0;\n/* unterminated").tokenize()

    def test_multiline_comment_with_stars(self):
        tokens = Tokenizer("/* ** stars ** */").tokenize()
        assert tokens == []

    def test_multiline_comment_empty(self):
        tokens = Tokenizer("/**/").tokenize()
        assert tokens == []

    def test_multiline_comment_at_end_of_file(self):
        tokens = Tokenizer("exit 0;\n/* trailing */").tokenize()
        assert len(tokens) == 3


class TestTokenizerStopChars:
    def test_identifier_modulo_no_spaces(self):
        from tokenizer.keywords import MODULO_KEYWORD
        tokens = Tokenizer("x%3;").tokenize()
        assert len(tokens) == 4
        assert isinstance(tokens[0], IDENTIFIER)
        assert tokens[0].val == "x"
        assert isinstance(tokens[1], MODULO_KEYWORD)
        assert isinstance(tokens[2], INT_LITERAL)
        assert tokens[2].val == 3
        assert isinstance(tokens[3], SEMICOLON)

    def test_identifier_int_division_no_spaces(self):
        from tokenizer.keywords import INT_DIVISION_KEYWORD
        tokens = Tokenizer("x//3;").tokenize()
        assert len(tokens) == 4
        assert isinstance(tokens[0], IDENTIFIER)
        assert tokens[0].val == "x"
        assert isinstance(tokens[1], INT_DIVISION_KEYWORD)
        assert isinstance(tokens[2], INT_LITERAL)
        assert tokens[2].val == 3
        assert isinstance(tokens[3], SEMICOLON)

    def test_number_modulo_no_spaces(self):
        from tokenizer.keywords import MODULO_KEYWORD
        tokens = Tokenizer("10%3;").tokenize()
        assert len(tokens) == 4
        assert isinstance(tokens[0], INT_LITERAL)
        assert tokens[0].val == 10
        assert isinstance(tokens[1], MODULO_KEYWORD)
        assert isinstance(tokens[2], INT_LITERAL)
        assert tokens[2].val == 3

    def test_number_int_division_no_spaces(self):
        from tokenizer.keywords import INT_DIVISION_KEYWORD
        tokens = Tokenizer("10//3;").tokenize()
        assert len(tokens) == 4
        assert isinstance(tokens[0], INT_LITERAL)
        assert tokens[0].val == 10
        assert isinstance(tokens[1], INT_DIVISION_KEYWORD)
        assert isinstance(tokens[2], INT_LITERAL)
        assert tokens[2].val == 3
