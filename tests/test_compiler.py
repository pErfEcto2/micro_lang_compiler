import pytest
from compiler.compiler import Compiler
from parser.program import PROGRAM
from parser.statements import ASSIGN_STATEMENT, CLOSE_C_STATEMENT, CONST_STATEMENT, EXIT_STATEMENT, IF_STATEMENT, INT64_STATEMENT, OPEN_C_STATEMENT, POSTFIX_STATEMENT, PREFIX_STATEMENT, PRINT_STATEMENT, STATEMENT
from parser.expressions import BINARY_EXPRESSION, IDENTIFIER_EXPRESSION, INT_EXPRESSION, POSTFIX_EXPRESSION, PREFIX_EXPRESSION, STR_EXPRESSION
from tokenizer.keywords import DECREMENT_KEYWORD, EQUALS_KEYWORD, GREATER_KEYWORD, GREATER_OR_EQUALS_KEYWORD, INCREMENT_KEYWORD, INT_DIVISION_KEYWORD, LESS_KEYWORD, LESS_OR_EQUALS_KEYWORD, MINUS_KEYWORD, MODULO_KEYWORD, MULTIPLY_KEYWORD, NOT_EQUALS_KEYWORD, PLUS_KEYWORD


def _make_program(*statements):
    prog = PROGRAM()
    prog.statements.extend(statements)
    return prog


class TestCompilerPrefix:
    def test_has_global_main(self):
        result = Compiler(_make_program()).compile()
        assert "global main" in result

    def test_has_text_section(self):
        result = Compiler(_make_program()).compile()
        assert "section .text" in result

    def test_has_data_section(self):
        result = Compiler(_make_program()).compile()
        assert "section .data" in result

    def test_has_main_label(self):
        result = Compiler(_make_program()).compile()
        assert "main:" in result

    def test_has_stack_frame_setup(self):
        result = Compiler(_make_program()).compile()
        assert "    push rbp" in result
        assert "    mov rbp, rsp" in result

    def test_prefix_order(self):
        result = Compiler(_make_program()).compile()
        lines = result.split("\n")
        assert lines[0] == "section .data"
        assert lines[1] == '    int_fmt_str db "%d", 10, 0'
        assert lines[2] == "section .text"
        assert lines[3] == "global main"
        assert lines[4] == "main:"
        assert lines[5] == "    push rbp"
        assert lines[6] == "    mov rbp, rsp"


class TestCompilerSuffix:
    def test_suffix_has_exit_syscall(self):
        result = Compiler(_make_program()).compile()
        lines = result.split("\n")
        assert "    mov rax, 60" in lines
        assert "    mov rdi, 0" in lines

    def test_suffix_ends_with_syscall(self):
        result = Compiler(_make_program()).compile()
        lines = [l for l in result.split("\n") if l.strip()]
        assert lines[-1].strip() == "syscall"


class TestCompilerExitStatement:
    def test_exit_with_int(self):
        prog = _make_program(EXIT_STATEMENT(1, INT_EXPRESSION(1, 69)))
        result = Compiler(prog).compile()
        assert "    push 69" in result
        assert "    pop rdi" in result
        assert "    mov rax, 60" in result
        assert "    syscall" in result

    def test_exit_with_zero(self):
        prog = _make_program(EXIT_STATEMENT(1, INT_EXPRESSION(1, 0)))
        result = Compiler(prog).compile()
        assert "    push 0" in result
        assert "    pop rdi" in result

    def test_exit_with_large_int(self):
        prog = _make_program(EXIT_STATEMENT(1, INT_EXPRESSION(1, 255)))
        result = Compiler(prog).compile()
        assert "    push 255" in result
        assert "    pop rdi" in result

    def test_exit_with_str_raises(self):
        prog = _make_program(EXIT_STATEMENT(1, STR_EXPRESSION(1, "hello")))
        with pytest.raises(ValueError, match="unexpected expression"):
            Compiler(prog).compile()

    def test_exit_str_error_reports_line(self):
        prog = _make_program(EXIT_STATEMENT(5, STR_EXPRESSION(5, "x")))
        with pytest.raises(ValueError, match="line 5"):
            Compiler(prog).compile()


class TestCompilerMultipleStatements:
    def test_two_exits(self):
        prog = _make_program(
            EXIT_STATEMENT(1, INT_EXPRESSION(1, 1)),
            EXIT_STATEMENT(2, INT_EXPRESSION(2, 2)),
        )
        result = Compiler(prog).compile()
        assert "    push 1" in result
        assert "    push 2" in result

    def test_exit_syscall_count(self):
        prog = _make_program(
            EXIT_STATEMENT(1, INT_EXPRESSION(1, 10)),
            EXIT_STATEMENT(2, INT_EXPRESSION(2, 20)),
        )
        result = Compiler(prog).compile()
        # 2 exit statements + 1 suffix = 3 syscalls
        assert result.count("    syscall") == 3
        # 2 exit statements + 1 suffix = 3 mov rax, 60
        assert result.count("    mov rax, 60") == 3


class TestCompilerFullOutput:
    def test_empty_program(self):
        result = Compiler(_make_program()).compile()
        expected = "\n".join([
            "section .data",
            '    int_fmt_str db "%d", 10, 0',
            "section .text",
            "global main",
            "main:",
            "    push rbp",
            "    mov rbp, rsp",
            "    mov rax, 60",
            "    mov rdi, 0",
            "    syscall",
        ])
        assert result == expected

    def test_single_exit(self):
        prog = _make_program(EXIT_STATEMENT(1, INT_EXPRESSION(1, 42)))
        result = Compiler(prog).compile()
        expected = "\n".join([
            "section .data",
            '    int_fmt_str db "%d", 10, 0',
            "section .text",
            "global main",
            "main:",
            "    push rbp",
            "    mov rbp, rsp",
            "    push 42",
            "    pop rdi",
            "    mov rax, 60",
            "    syscall",
            "    mov rax, 60",
            "    mov rdi, 0",
            "    syscall",
        ])
        assert result == expected


class TestCompilerHelpers:
    def test_push(self):
        c = Compiler(_make_program())
        c._push("rax")
        assert "    push rax" in c._text_s

    def test_pop(self):
        c = Compiler(_make_program())
        c._pop("rbx")
        assert "    pop rbx" in c._text_s

    def test_add(self):
        c = Compiler(_make_program())
        c._add("rax", "rbx")
        assert "    add rax, rbx" in c._text_s

    def test_imul(self):
        c = Compiler(_make_program())
        c._imul("rax", "rbx")
        assert "    imul rax, rbx" in c._text_s

    def test_sub(self):
        c = Compiler(_make_program())
        c._sub("rax", "rbx")
        assert "    sub rax, rbx" in c._text_s

    def test_idiv(self):
        c = Compiler(_make_program())
        c._idiv("rbx")
        assert "    idiv rbx" in c._text_s

    def test_cqo(self):
        c = Compiler(_make_program())
        c._cqo()
        assert "    cqo" in c._text_s

    def test_lea(self):
        c = Compiler(_make_program())
        c._lea("rdi", "[int_fmt_str]")
        assert "    lea rdi, [int_fmt_str]" in c._text_s

    def test_call(self):
        c = Compiler(_make_program())
        c._call("printf")
        assert "    call printf" in c._text_s


class TestCompilerErrors:
    def test_unexpected_statement_type(self):
        prog = _make_program(STATEMENT(1))
        with pytest.raises(ValueError, match="unexpected statement"):
            Compiler(prog).compile()

    def test_unexpected_statement_reports_line(self):
        prog = _make_program(STATEMENT(7))
        with pytest.raises(ValueError, match="line 7"):
            Compiler(prog).compile()


class TestCompilerBinaryExpressions:
    def test_addition(self):
        expr = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 10), PLUS_KEYWORD(1), INT_EXPRESSION(1, 20))
        prog = _make_program(EXIT_STATEMENT(1, expr))
        result = Compiler(prog).compile()
        assert "    push 20" in result
        assert "    push 10" in result
        assert "    add rax, rbx" in result

    def test_subtraction(self):
        expr = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 10), MINUS_KEYWORD(1), INT_EXPRESSION(1, 3))
        prog = _make_program(EXIT_STATEMENT(1, expr))
        result = Compiler(prog).compile()
        assert "    push 3" in result
        assert "    push 10" in result
        assert "    sub rax, rbx" in result

    def test_multiplication(self):
        expr = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 3), MULTIPLY_KEYWORD(1), INT_EXPRESSION(1, 4))
        prog = _make_program(EXIT_STATEMENT(1, expr))
        result = Compiler(prog).compile()
        assert "    push 4" in result
        assert "    push 3" in result
        assert "    imul rax, rbx" in result

    def test_int_division(self):
        expr = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 10), INT_DIVISION_KEYWORD(1), INT_EXPRESSION(1, 3))
        prog = _make_program(EXIT_STATEMENT(1, expr))
        result = Compiler(prog).compile()
        assert "    cqo" in result
        assert "    idiv rbx" in result
        assert "    push rax" in result

    def test_modulo(self):
        expr = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 10), MODULO_KEYWORD(1), INT_EXPRESSION(1, 3))
        prog = _make_program(EXIT_STATEMENT(1, expr))
        result = Compiler(prog).compile()
        assert "    cqo" in result
        assert "    idiv rbx" in result
        assert "    push rdx" in result

    def test_nested_expression(self):
        # 1 + 2 * 3 → BINARY(1, +, BINARY(2, *, 3))
        inner = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 2), MULTIPLY_KEYWORD(1), INT_EXPRESSION(1, 3))
        outer = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 1), PLUS_KEYWORD(1), inner)
        prog = _make_program(EXIT_STATEMENT(1, outer))
        result = Compiler(prog).compile()
        assert "    imul rax, rbx" in result
        assert "    add rax, rbx" in result


class TestCompilerComparisonExpressions:
    def test_greater_than(self):
        expr = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 5), GREATER_KEYWORD(1), INT_EXPRESSION(1, 3))
        prog = _make_program(EXIT_STATEMENT(1, expr))
        result = Compiler(prog).compile()
        assert "    cmp rax, rbx" in result
        assert "    setg al" in result
        assert "    movzx rax, al" in result

    def test_less_than(self):
        expr = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 3), LESS_KEYWORD(1), INT_EXPRESSION(1, 5))
        prog = _make_program(EXIT_STATEMENT(1, expr))
        result = Compiler(prog).compile()
        assert "    cmp rax, rbx" in result
        assert "    setl al" in result
        assert "    movzx rax, al" in result

    def test_greater_or_equals(self):
        expr = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 5), GREATER_OR_EQUALS_KEYWORD(1), INT_EXPRESSION(1, 5))
        prog = _make_program(EXIT_STATEMENT(1, expr))
        result = Compiler(prog).compile()
        assert "    cmp rax, rbx" in result
        assert "    setge al" in result
        assert "    movzx rax, al" in result

    def test_less_or_equals(self):
        expr = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 3), LESS_OR_EQUALS_KEYWORD(1), INT_EXPRESSION(1, 5))
        prog = _make_program(EXIT_STATEMENT(1, expr))
        result = Compiler(prog).compile()
        assert "    cmp rax, rbx" in result
        assert "    setle al" in result
        assert "    movzx rax, al" in result

    def test_equals(self):
        expr = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 5), EQUALS_KEYWORD(1), INT_EXPRESSION(1, 5))
        prog = _make_program(EXIT_STATEMENT(1, expr))
        result = Compiler(prog).compile()
        assert "    cmp rax, rbx" in result
        assert "    sete al" in result
        assert "    movzx rax, al" in result

    def test_not_equals(self):
        expr = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 5), NOT_EQUALS_KEYWORD(1), INT_EXPRESSION(1, 3))
        prog = _make_program(EXIT_STATEMENT(1, expr))
        result = Compiler(prog).compile()
        assert "    cmp rax, rbx" in result
        assert "    setne al" in result
        assert "    movzx rax, al" in result

    def test_equals_pushes_result(self):
        expr = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 1), EQUALS_KEYWORD(1), INT_EXPRESSION(1, 1))
        prog = _make_program(EXIT_STATEMENT(1, expr))
        result = Compiler(prog).compile()
        lines = result.split("\n")
        movzx_idx = next(i for i, l in enumerate(lines) if "movzx rax, al" in l)
        assert "push rax" in lines[movzx_idx + 1]

    def test_not_equals_pushes_result(self):
        expr = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 1), NOT_EQUALS_KEYWORD(1), INT_EXPRESSION(1, 2))
        prog = _make_program(EXIT_STATEMENT(1, expr))
        result = Compiler(prog).compile()
        lines = result.split("\n")
        movzx_idx = next(i for i, l in enumerate(lines) if "movzx rax, al" in l)
        assert "push rax" in lines[movzx_idx + 1]


class TestCompilerComparisonIntegration:
    def test_full_pipeline_equals(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("exit 5 == 5;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    sete al" in result
        assert "    pop rdi" in result

    def test_full_pipeline_not_equals(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("exit 5 != 3;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    setne al" in result
        assert "    pop rdi" in result

    def test_full_pipeline_equals_in_if(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("if (1 == 1) { print 42; }").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    sete al" in result
        assert "    cmp rax, 0" in result
        assert "    call printf" in result

    def test_full_pipeline_not_equals_in_if(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("if (1 != 0) { print 42; }").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    setne al" in result
        assert "    cmp rax, 0" in result
        assert "    call printf" in result

    def test_full_pipeline_equals_with_vars(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("int64 x = 5;\nint64 y = 5;\nif (x == y) { print 1; }").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    sete al" in result
        assert "    call printf" in result

    def test_full_pipeline_not_equals_in_while(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("int64 x = 3;\nwhile (x != 0) { x = x - 1; }").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    setne al" in result
        assert ".while_start_0:" in result
        assert ".while_end_0:" in result

    def test_equals_lower_precedence_than_arithmetic(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("exit 1 + 2 == 3;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    add rax, rbx" in result
        assert "    sete al" in result


class TestCompilerInt64Statement:
    def test_simple_int64(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5))
        )
        result = Compiler(prog).compile()
        assert "    sub rsp, 8" in result
        assert "    push 5" in result
        assert "    pop rax" in result
        assert "    mov qword [rbp - 8], rax" in result

    def test_int64_and_exit_with_var(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 42)),
            EXIT_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "x")),
        )
        result = Compiler(prog).compile()
        assert "    mov qword [rbp - 8], rax" in result
        assert "    mov rax, qword [rbp - 8]" in result
        assert "    pop rdi" in result

    def test_two_vars_different_offsets(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "a"), INT_EXPRESSION(1, 1)),
            INT64_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "b"), INT_EXPRESSION(2, 2)),
        )
        result = Compiler(prog).compile()
        assert "    mov qword [rbp - 8], rax" in result
        assert "    mov qword [rbp - 16], rax" in result

    def test_duplicate_var_raises(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 1)),
            INT64_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "x"), INT_EXPRESSION(2, 2)),
        )
        with pytest.raises(ValueError, match="already exists"):
            Compiler(prog).compile()

    def test_unknown_identifier_raises(self):
        prog = _make_program(
            EXIT_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "unknown")),
        )
        with pytest.raises(ValueError, match="unknown identifier"):
            Compiler(prog).compile()


class TestCompilerIntegration:
    def test_full_pipeline_exit(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("exit 69;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "global main" in result
        assert "push 69" in result
        assert "pop rdi" in result
        assert "syscall" in result

    def test_full_pipeline_multiple_exits(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("exit 69;\nexit 70;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "push 69" in result
        assert "push 70" in result

    def test_full_pipeline_empty(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "global main" in result
        assert "    mov rax, 60" in result

    def test_full_pipeline_arithmetic(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("exit 1 + 2;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    add rax, rbx" in result
        assert "    pop rdi" in result

    def test_full_pipeline_int64_and_exit(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("int64 x = 42;\nexit x;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    mov qword [rbp - 8], rax" in result
        assert "    mov rax, qword [rbp - 8]" in result
        assert "    pop rdi" in result

    def test_full_pipeline_subtraction(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("exit 10 - 3;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    sub rax, rbx" in result

    def test_full_pipeline_int64_with_expression(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("int64 a = 60 + 2 * 4;\nexit a;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    imul rax, rbx" in result
        assert "    add rax, rbx" in result
        assert "    pop rdi" in result

    def test_full_pipeline_print(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("print 42;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "extern printf" in result
        assert "    call printf" in result

    def test_full_pipeline_assign(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("int64 x = 1;\nx = 10;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    mov qword [rbp - 8], rax" in result


class TestCompilerPrintStatement:
    def test_print_int(self):
        prog = _make_program(PRINT_STATEMENT(1, INT_EXPRESSION(1, 42)))
        result = Compiler(prog).compile()
        assert "extern printf" in result
        assert "    push 42" in result
        assert "    pop rsi" in result
        assert '    lea rdi, [int_fmt_str]' in result
        assert "    mov rax, 0" in result
        assert "    call printf" in result

    def test_print_var(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5)),
            PRINT_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "x")),
        )
        result = Compiler(prog).compile()
        assert "extern printf" in result
        assert "    call printf" in result

    def test_print_expression(self):
        expr = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 10), PLUS_KEYWORD(1), INT_EXPRESSION(1, 20))
        prog = _make_program(PRINT_STATEMENT(1, expr))
        result = Compiler(prog).compile()
        assert "    add rax, rbx" in result
        assert "    pop rsi" in result
        assert "    call printf" in result

    def test_no_extern_without_print(self):
        prog = _make_program(EXIT_STATEMENT(1, INT_EXPRESSION(1, 0)))
        result = Compiler(prog).compile()
        assert "extern" not in result


class TestCompilerAssignStatement:
    def test_simple_assign(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5)),
            ASSIGN_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "x"), INT_EXPRESSION(2, 10)),
        )
        result = Compiler(prog).compile()
        assert result.count("    mov qword [rbp - 8], rax") == 2

    def test_assign_with_expression(self):
        expr = BINARY_EXPRESSION(2, IDENTIFIER_EXPRESSION(2, "x"), PLUS_KEYWORD(2), INT_EXPRESSION(2, 1))
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5)),
            ASSIGN_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "x"), expr),
        )
        result = Compiler(prog).compile()
        assert "    add rax, rbx" in result

    def test_assign_unknown_var_raises(self):
        prog = _make_program(
            ASSIGN_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "y"), INT_EXPRESSION(1, 1)),
        )
        with pytest.raises(ValueError, match="unknown identifier"):
            Compiler(prog).compile()


class TestCompilerConstStatement:
    def test_simple_const(self):
        inner = INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5))
        prog = _make_program(CONST_STATEMENT(1, inner))
        result = Compiler(prog).compile()
        assert "    sub rsp, 8" in result
        assert "    push 5" in result
        assert "    pop rax" in result
        assert "    mov qword [rbp - 8], rax" in result

    def test_const_used_in_expression(self):
        inner = INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 42))
        prog = _make_program(
            CONST_STATEMENT(1, inner),
            EXIT_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "x")),
        )
        result = Compiler(prog).compile()
        assert "    mov rax, qword [rbp - 8]" in result
        assert "    pop rdi" in result

    def test_const_reassign_raises(self):
        inner = INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5))
        prog = _make_program(
            CONST_STATEMENT(1, inner),
            ASSIGN_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "x"), INT_EXPRESSION(2, 10)),
        )
        with pytest.raises(ValueError, match="cant change constant"):
            Compiler(prog).compile()

    def test_const_duplicate_raises(self):
        inner1 = INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 1))
        inner2 = INT64_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "x"), INT_EXPRESSION(2, 2))
        prog = _make_program(
            CONST_STATEMENT(1, inner1),
            CONST_STATEMENT(2, inner2),
        )
        with pytest.raises(ValueError, match="already exists"):
            Compiler(prog).compile()

    def test_const_conflicts_with_var_raises(self):
        inner = INT64_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "x"), INT_EXPRESSION(2, 2))
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 1)),
            CONST_STATEMENT(2, inner),
        )
        with pytest.raises(ValueError, match="already exists"):
            Compiler(prog).compile()

    def test_full_pipeline_const(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("const int64 x = 42;\nexit x;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    mov qword [rbp - 8], rax" in result
        assert "    pop rdi" in result


class TestCompilerScopeStatement:
    def test_empty_scope(self):
        prog = _make_program(
            OPEN_C_STATEMENT(1),
            CLOSE_C_STATEMENT(2),
        )
        result = Compiler(prog).compile()
        assert "    add rsp," not in result

    def test_scope_with_var(self):
        prog = _make_program(
            OPEN_C_STATEMENT(1),
            INT64_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "x"), INT_EXPRESSION(2, 5)),
            CLOSE_C_STATEMENT(3),
        )
        result = Compiler(prog).compile()
        assert "    sub rsp, 8" in result
        assert "    mov qword [rbp - 8], rax" in result
        assert "    add rsp, 8" in result

    def test_var_shadowing_in_scope(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 10)),
            OPEN_C_STATEMENT(2),
            INT64_STATEMENT(3, IDENTIFIER_EXPRESSION(3, "x"), INT_EXPRESSION(3, 20)),
            CLOSE_C_STATEMENT(4),
        )
        result = Compiler(prog).compile()
        assert "    mov qword [rbp - 8], rax" in result
        assert "    mov qword [rbp - 16], rax" in result

    def test_outer_var_accessible_from_inner_scope(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 42)),
            OPEN_C_STATEMENT(2),
            PRINT_STATEMENT(3, IDENTIFIER_EXPRESSION(3, "x")),
            CLOSE_C_STATEMENT(4),
        )
        result = Compiler(prog).compile()
        assert "    mov rax, qword [rbp - 8]" in result
        assert "    call printf" in result

    def test_unclosed_scope_raises(self):
        prog = _make_program(
            OPEN_C_STATEMENT(1),
            INT64_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "x"), INT_EXPRESSION(2, 5)),
        )
        with pytest.raises(ValueError, match="never closed"):
            Compiler(prog).compile()

    def test_const_in_scope(self):
        inner = INT64_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "y"), INT_EXPRESSION(2, 99))
        prog = _make_program(
            OPEN_C_STATEMENT(1),
            CONST_STATEMENT(2, inner),
            CLOSE_C_STATEMENT(3),
        )
        result = Compiler(prog).compile()
        assert "    mov qword [rbp - 8], rax" in result
        assert "    add rsp, 8" in result

    def test_assign_outer_var_from_inner_scope(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 1)),
            OPEN_C_STATEMENT(2),
            ASSIGN_STATEMENT(3, IDENTIFIER_EXPRESSION(3, "x"), INT_EXPRESSION(3, 99)),
            CLOSE_C_STATEMENT(4),
        )
        result = Compiler(prog).compile()
        assert result.count("    mov qword [rbp - 8], rax") == 2

    def test_assign_outer_const_from_inner_scope_raises(self):
        inner = INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 1))
        prog = _make_program(
            CONST_STATEMENT(1, inner),
            OPEN_C_STATEMENT(2),
            ASSIGN_STATEMENT(3, IDENTIFIER_EXPRESSION(3, "x"), INT_EXPRESSION(3, 99)),
            CLOSE_C_STATEMENT(4),
        )
        with pytest.raises(ValueError, match="cant change constant"):
            Compiler(prog).compile()

    def test_full_pipeline_scope(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("int64 a = 1;\n{ int64 b = 2;\nprint b; }\nprint a;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    add rsp, 8" in result
        assert result.count("    call printf") == 2

    def test_full_pipeline_shadowing(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("int64 a = 60;\n{ int64 a = 1;\nprint a; }\nprint a;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    mov qword [rbp - 8], rax" in result
        assert "    mov qword [rbp - 16], rax" in result

    def test_assign_var_shadowing_outer_const(self):
        """inner var shadows outer const — assigning to inner var should succeed"""
        const_inner = INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 10))
        prog = _make_program(
            CONST_STATEMENT(1, const_inner),
            OPEN_C_STATEMENT(2),
            INT64_STATEMENT(3, IDENTIFIER_EXPRESSION(3, "x"), INT_EXPRESSION(3, 20)),
            ASSIGN_STATEMENT(4, IDENTIFIER_EXPRESSION(4, "x"), INT_EXPRESSION(4, 30)),
            CLOSE_C_STATEMENT(5),
        )
        result = Compiler(prog).compile()
        assert "    mov qword [rbp - 8], rax" in result   # outer const x
        assert "    mov qword [rbp - 16], rax" in result  # inner var x (decl + assign)


class TestCompilerIfStatement:
    def test_simple_if_generates_labels(self):
        prog = _make_program(
            IF_STATEMENT(1, INT_EXPRESSION(1, 1), [
                OPEN_C_STATEMENT(1),
                PRINT_STATEMENT(2, INT_EXPRESSION(2, 42)),
                CLOSE_C_STATEMENT(3),
            ]),
        )
        result = Compiler(prog).compile()
        assert ".if_end_0:" in result

    def test_if_evaluates_condition(self):
        prog = _make_program(
            IF_STATEMENT(1, INT_EXPRESSION(1, 5), [
                OPEN_C_STATEMENT(1),
                CLOSE_C_STATEMENT(2),
            ]),
        )
        result = Compiler(prog).compile()
        assert "    push 5" in result
        assert "    pop rax" in result
        assert "    cmp rax, 0" in result

    def test_if_without_else_uses_je_to_end(self):
        prog = _make_program(
            IF_STATEMENT(1, INT_EXPRESSION(1, 1), [
                OPEN_C_STATEMENT(1),
                CLOSE_C_STATEMENT(2),
            ]),
        )
        result = Compiler(prog).compile()
        assert "    je .if_end_0" in result
        assert ".if_end_0:" in result
        assert ".else_0:" not in result

    def test_if_with_print_in_body(self):
        prog = _make_program(
            IF_STATEMENT(1, INT_EXPRESSION(1, 1), [
                OPEN_C_STATEMENT(1),
                PRINT_STATEMENT(2, INT_EXPRESSION(2, 42)),
                CLOSE_C_STATEMENT(3),
            ]),
        )
        result = Compiler(prog).compile()
        assert "    call printf" in result
        assert "    push 42" in result

    def test_if_with_var_condition(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 10)),
            IF_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "x"), [
                OPEN_C_STATEMENT(2),
                PRINT_STATEMENT(3, INT_EXPRESSION(3, 1)),
                CLOSE_C_STATEMENT(4),
            ]),
        )
        result = Compiler(prog).compile()
        assert "    mov rax, qword [rbp - 8]" in result
        assert "    cmp rax, 0" in result

    def test_if_with_expression_condition(self):
        expr = BINARY_EXPRESSION(1, INT_EXPRESSION(1, 3), PLUS_KEYWORD(1), INT_EXPRESSION(1, 4))
        prog = _make_program(
            IF_STATEMENT(1, expr, [
                OPEN_C_STATEMENT(1),
                CLOSE_C_STATEMENT(2),
            ]),
        )
        result = Compiler(prog).compile()
        assert "    add rax, rbx" in result
        assert "    cmp rax, 0" in result

    def test_if_empty_body(self):
        prog = _make_program(
            IF_STATEMENT(1, INT_EXPRESSION(1, 1), [
                OPEN_C_STATEMENT(1),
                CLOSE_C_STATEMENT(1),
            ]),
        )
        result = Compiler(prog).compile()
        assert "    je .if_end_0" in result
        assert ".if_end_0:" in result


class TestCompilerIfElseStatement:
    def test_if_else_generates_both_labels(self):
        prog = _make_program(
            IF_STATEMENT(1, INT_EXPRESSION(1, 1), [
                OPEN_C_STATEMENT(1),
                PRINT_STATEMENT(2, INT_EXPRESSION(2, 10)),
                CLOSE_C_STATEMENT(3),
            ], [
                OPEN_C_STATEMENT(3),
                PRINT_STATEMENT(4, INT_EXPRESSION(4, 20)),
                CLOSE_C_STATEMENT(5),
            ]),
        )
        result = Compiler(prog).compile()
        assert ".else_0:" in result
        assert ".if_end_0:" in result

    def test_if_else_uses_je_to_else(self):
        prog = _make_program(
            IF_STATEMENT(1, INT_EXPRESSION(1, 1), [
                OPEN_C_STATEMENT(1),
                CLOSE_C_STATEMENT(2),
            ], [
                OPEN_C_STATEMENT(2),
                CLOSE_C_STATEMENT(3),
            ]),
        )
        result = Compiler(prog).compile()
        assert "    je .else_0" in result
        assert "    jmp .if_end_0" in result

    def test_if_else_true_body_has_print(self):
        prog = _make_program(
            IF_STATEMENT(1, INT_EXPRESSION(1, 1), [
                OPEN_C_STATEMENT(1),
                PRINT_STATEMENT(2, INT_EXPRESSION(2, 10)),
                CLOSE_C_STATEMENT(3),
            ], [
                OPEN_C_STATEMENT(3),
                PRINT_STATEMENT(4, INT_EXPRESSION(4, 20)),
                CLOSE_C_STATEMENT(5),
            ]),
        )
        result = Compiler(prog).compile()
        assert "    push 10" in result
        assert "    push 20" in result

    def test_if_else_both_empty(self):
        prog = _make_program(
            IF_STATEMENT(1, INT_EXPRESSION(1, 1), [
                OPEN_C_STATEMENT(1),
                CLOSE_C_STATEMENT(1),
            ], [
                OPEN_C_STATEMENT(1),
                CLOSE_C_STATEMENT(1),
            ]),
        )
        result = Compiler(prog).compile()
        assert "    je .else_0" in result
        assert ".else_0:" in result
        assert ".if_end_0:" in result

    def test_if_else_with_var_declarations(self):
        prog = _make_program(
            IF_STATEMENT(1, INT_EXPRESSION(1, 1), [
                OPEN_C_STATEMENT(1),
                INT64_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "a"), INT_EXPRESSION(2, 10)),
                PRINT_STATEMENT(3, IDENTIFIER_EXPRESSION(3, "a")),
                CLOSE_C_STATEMENT(4),
            ], [
                OPEN_C_STATEMENT(4),
                INT64_STATEMENT(5, IDENTIFIER_EXPRESSION(5, "b"), INT_EXPRESSION(5, 20)),
                PRINT_STATEMENT(6, IDENTIFIER_EXPRESSION(6, "b")),
                CLOSE_C_STATEMENT(7),
            ]),
        )
        result = Compiler(prog).compile()
        assert "    push 10" in result
        assert "    push 20" in result
        assert "    call printf" in result


class TestCompilerNestedIf:
    def test_nested_if_generates_separate_labels(self):
        prog = _make_program(
            IF_STATEMENT(1, INT_EXPRESSION(1, 1), [
                OPEN_C_STATEMENT(1),
                IF_STATEMENT(2, INT_EXPRESSION(2, 1), [
                    OPEN_C_STATEMENT(2),
                    PRINT_STATEMENT(3, INT_EXPRESSION(3, 42)),
                    CLOSE_C_STATEMENT(4),
                ]),
                CLOSE_C_STATEMENT(5),
            ]),
        )
        result = Compiler(prog).compile()
        assert ".if_end_0:" in result
        assert ".if_end_1:" in result

    def test_nested_if_else_in_true_body(self):
        prog = _make_program(
            IF_STATEMENT(1, INT_EXPRESSION(1, 1), [
                OPEN_C_STATEMENT(1),
                IF_STATEMENT(2, INT_EXPRESSION(2, 0), [
                    OPEN_C_STATEMENT(2),
                    PRINT_STATEMENT(3, INT_EXPRESSION(3, 1)),
                    CLOSE_C_STATEMENT(4),
                ], [
                    OPEN_C_STATEMENT(4),
                    PRINT_STATEMENT(5, INT_EXPRESSION(5, 2)),
                    CLOSE_C_STATEMENT(6),
                ]),
                CLOSE_C_STATEMENT(7),
            ]),
        )
        result = Compiler(prog).compile()
        assert ".else_1:" in result
        assert ".if_end_1:" in result
        assert ".if_end_0:" in result

    def test_nested_if_in_else_body(self):
        prog = _make_program(
            IF_STATEMENT(1, INT_EXPRESSION(1, 0), [
                OPEN_C_STATEMENT(1),
                PRINT_STATEMENT(2, INT_EXPRESSION(2, 1)),
                CLOSE_C_STATEMENT(3),
            ], [
                OPEN_C_STATEMENT(3),
                IF_STATEMENT(4, INT_EXPRESSION(4, 1), [
                    OPEN_C_STATEMENT(4),
                    PRINT_STATEMENT(5, INT_EXPRESSION(5, 2)),
                    CLOSE_C_STATEMENT(6),
                ]),
                CLOSE_C_STATEMENT(7),
            ]),
        )
        result = Compiler(prog).compile()
        assert ".else_0:" in result
        assert ".if_end_0:" in result
        assert ".if_end_1:" in result

    def test_multiple_ifs_get_separate_labels(self):
        prog = _make_program(
            IF_STATEMENT(1, INT_EXPRESSION(1, 1), [
                OPEN_C_STATEMENT(1),
                PRINT_STATEMENT(2, INT_EXPRESSION(2, 1)),
                CLOSE_C_STATEMENT(3),
            ]),
            IF_STATEMENT(4, INT_EXPRESSION(4, 0), [
                OPEN_C_STATEMENT(4),
                PRINT_STATEMENT(5, INT_EXPRESSION(5, 2)),
                CLOSE_C_STATEMENT(6),
            ]),
        )
        result = Compiler(prog).compile()
        assert ".if_end_0:" in result
        assert ".if_end_1:" in result


class TestCompilerIfIntegration:
    def test_full_pipeline_simple_if(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("if (1) { print 42; }").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    cmp rax, 0" in result
        assert "    je .if_end_0" in result
        assert "    call printf" in result
        assert ".if_end_0:" in result

    def test_full_pipeline_if_else(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("if (0) { print 1; } else { print 2; }").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    je .else_0" in result
        assert "    jmp .if_end_0" in result
        assert ".else_0:" in result
        assert ".if_end_0:" in result

    def test_full_pipeline_if_with_var(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("int64 x = 1;\nif (x) { print 42; }").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    cmp rax, 0" in result
        assert "    call printf" in result

    def test_full_pipeline_if_with_expression_condition(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("if (1 + 2) { print 99; }").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    add rax, rbx" in result
        assert "    cmp rax, 0" in result

    def test_full_pipeline_nested_if_else(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        src = "if (1) { if (0) { print 1; } else { print 2; } } else { print 3; }"
        tokens = Tokenizer(src).tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert ".else_0:" in result
        assert ".if_end_0:" in result
        assert ".else_1:" in result
        assert ".if_end_1:" in result

    def test_full_pipeline_if_with_var_declaration(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("if (1) { int64 x = 42; print x; }").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    sub rsp, 8" in result
        assert "    add rsp, 8" in result
        assert "    call printf" in result

    def test_full_pipeline_if_with_outer_var(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("int64 x = 10;\nif (x) { print x; }").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert result.count("    mov rax, qword [rbp - 8]") >= 2

    def test_full_pipeline_if_else_with_assign(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        src = "int64 x = 1;\nif (x) { x = 10; } else { x = 20; }\nprint x;"
        tokens = Tokenizer(src).tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    call printf" in result
        assert ".else_0:" in result
        assert ".if_end_0:" in result

    def test_full_pipeline_multiple_sequential_ifs(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        src = "if (1) { print 1; }\nif (1) { print 2; }\nif (0) { print 3; }"
        tokens = Tokenizer(src).tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert ".if_end_0:" in result
        assert ".if_end_1:" in result
        assert ".if_end_2:" in result

    def test_full_pipeline_deeply_nested_if(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        src = "if (1) { if (1) { if (1) { print 42; } } }"
        tokens = Tokenizer(src).tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert ".if_end_0:" in result
        assert ".if_end_1:" in result
        assert ".if_end_2:" in result
        assert "    push 42" in result


class TestCompilerWhileStatement:
    def test_while_body_has_scope_cleanup(self):
        """While loop body with variable should clean up stack space"""
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        src = "int64 x = 0;\nwhile (x < 3) {\n  int64 y = 1;\n  x = x + 1;\n}"
        tokens = Tokenizer(src).tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        # The while body declares a variable (sub rsp, 8) so it must
        # clean up that stack space (add rsp, 8) before looping back
        body_start = result.index(".while_start_0:")
        body_end = result.index(".while_end_0:")
        body = result[body_start:body_end]
        assert "sub rsp, 8" in body
        assert "add rsp, 8" in body

    def test_while_with_var_after_loop(self):
        """Variables declared after a while loop should work correctly"""
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        src = "int64 x = 0;\nwhile (x < 2) {\n  int64 y = 1;\n  x = x + 1;\n}\nint64 z = 99;\nexit z;"
        tokens = Tokenizer(src).tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        # Should compile without scope corruption
        assert ".while_start_0:" in result
        assert ".while_end_0:" in result
        assert "push 99" in result

class TestCompilerIfHelpers:
    def test_cmp(self):
        c = Compiler(_make_program())
        c._cmp("rax", "0")
        assert "    cmp rax, 0" in c._text_s

    def test_je(self):
        c = Compiler(_make_program())
        c._je(".if_end_0")
        assert "    je .if_end_0" in c._text_s

    def test_jmp(self):
        c = Compiler(_make_program())
        c._jmp(".if_end_0")
        assert "    jmp .if_end_0" in c._text_s

    def test_label(self):
        c = Compiler(_make_program())
        c._label(".if_end_0")
        assert ".if_end_0:" in c._text_s

    def test_gen_label_increments(self):
        c = Compiler(_make_program())
        assert c._gen_label() == 0
        assert c._gen_label() == 1
        assert c._gen_label() == 2


class TestCompilerPostfixStatement:
    def test_postfix_increment_emits_inc(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 0)),
            POSTFIX_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INCREMENT_KEYWORD(1)),
        )
        result = Compiler(prog).compile()
        assert "inc qword [rbp - 8]" in result

    def test_postfix_decrement_emits_dec(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 0)),
            POSTFIX_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), DECREMENT_KEYWORD(1)),
        )
        result = Compiler(prog).compile()
        assert "dec qword [rbp - 8]" in result

    def test_postfix_on_undeclared_var_raises(self):
        prog = _make_program(
            POSTFIX_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INCREMENT_KEYWORD(1)),
        )
        with pytest.raises(ValueError, match="unknown identifier"):
            Compiler(prog).compile()

    def test_postfix_on_const_raises(self):
        prog = _make_program(
            CONST_STATEMENT(1, INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5))),
            POSTFIX_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INCREMENT_KEYWORD(1)),
        )
        with pytest.raises(ValueError, match="constant"):
            Compiler(prog).compile()


class TestCompilerPrefixStatement:
    def test_prefix_increment_emits_inc(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 0)),
            PREFIX_STATEMENT(1, INCREMENT_KEYWORD(1), IDENTIFIER_EXPRESSION(1, "x")),
        )
        result = Compiler(prog).compile()
        assert "inc qword [rbp - 8]" in result

    def test_prefix_decrement_emits_dec(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 0)),
            PREFIX_STATEMENT(1, DECREMENT_KEYWORD(1), IDENTIFIER_EXPRESSION(1, "x")),
        )
        result = Compiler(prog).compile()
        assert "dec qword [rbp - 8]" in result

    def test_prefix_on_undeclared_var_raises(self):
        prog = _make_program(
            PREFIX_STATEMENT(1, INCREMENT_KEYWORD(1), IDENTIFIER_EXPRESSION(1, "x")),
        )
        with pytest.raises(ValueError, match="unknown identifier"):
            Compiler(prog).compile()

    def test_prefix_on_const_raises(self):
        prog = _make_program(
            CONST_STATEMENT(1, INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5))),
            PREFIX_STATEMENT(1, INCREMENT_KEYWORD(1), IDENTIFIER_EXPRESSION(1, "x")),
        )
        with pytest.raises(ValueError, match="constant"):
            Compiler(prog).compile()


class TestCompilerPostfixExpression:
    def test_postfix_increment_expr_pushes_old_value_then_increments(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5)),
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "a"), POSTFIX_EXPRESSION(1, IDENTIFIER_EXPRESSION(1, "x"), INCREMENT_KEYWORD(1))),
        )
        result = Compiler(prog).compile()
        lines = result.split("\n")
        text = "\n".join(lines)
        assert "push qword [rbp - 8]" in text
        assert "inc qword [rbp - 8]" in text

    def test_postfix_decrement_expr_emits_dec(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5)),
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "a"), POSTFIX_EXPRESSION(1, IDENTIFIER_EXPRESSION(1, "x"), DECREMENT_KEYWORD(1))),
        )
        result = Compiler(prog).compile()
        assert "dec qword [rbp - 8]" in result

    def test_postfix_expr_on_const_raises(self):
        prog = _make_program(
            CONST_STATEMENT(1, INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5))),
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "a"), POSTFIX_EXPRESSION(1, IDENTIFIER_EXPRESSION(1, "x"), INCREMENT_KEYWORD(1))),
        )
        with pytest.raises(ValueError, match="constant"):
            Compiler(prog).compile()

    def test_postfix_expr_on_undeclared_raises(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "a"), POSTFIX_EXPRESSION(1, IDENTIFIER_EXPRESSION(1, "x"), INCREMENT_KEYWORD(1))),
        )
        with pytest.raises(ValueError, match="unknown identifier"):
            Compiler(prog).compile()


class TestCompilerPrefixExpression:
    def test_prefix_increment_expr_increments_then_pushes(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5)),
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "a"), PREFIX_EXPRESSION(1, INCREMENT_KEYWORD(1), IDENTIFIER_EXPRESSION(1, "x"))),
        )
        result = Compiler(prog).compile()
        lines = result.split("\n")
        text = "\n".join(lines)
        assert "inc qword [rbp - 8]" in text
        assert "push qword [rbp - 8]" in text

    def test_prefix_decrement_expr_emits_dec(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5)),
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "a"), PREFIX_EXPRESSION(1, DECREMENT_KEYWORD(1), IDENTIFIER_EXPRESSION(1, "x"))),
        )
        result = Compiler(prog).compile()
        assert "dec qword [rbp - 8]" in result

    def test_prefix_expr_on_const_raises(self):
        prog = _make_program(
            CONST_STATEMENT(1, INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5))),
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "a"), PREFIX_EXPRESSION(1, INCREMENT_KEYWORD(1), IDENTIFIER_EXPRESSION(1, "x"))),
        )
        with pytest.raises(ValueError, match="constant"):
            Compiler(prog).compile()

    def test_prefix_expr_on_undeclared_raises(self):
        prog = _make_program(
            INT64_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "a"), PREFIX_EXPRESSION(1, INCREMENT_KEYWORD(1), IDENTIFIER_EXPRESSION(1, "x"))),
        )
        with pytest.raises(ValueError, match="unknown identifier"):
            Compiler(prog).compile()

