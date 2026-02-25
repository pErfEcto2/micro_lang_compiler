import pytest
from compiler.compiler import Compiler
from parser.program import PROGRAM
from parser.statements import EXIT_STATEMENT, LET_STATEMENT, STATEMENT
from parser.expressions import BINARY_EXPRESSION, IDENTIFIER_EXPRESSION, INT_EXPRESSION, STR_EXPRESSION
from tokenizer.keywords import INT_DIVISION_KEYWORD, MINUS_KEYWORD, MODULO_KEYWORD, MULTIPLY_KEYWORD, PLUS_KEYWORD


def _make_program(*statements):
    prog = PROGRAM()
    prog.statements.extend(statements)
    return prog


class TestCompilerPrefix:
    def test_has_global_start(self):
        result = Compiler(_make_program()).compile()
        assert "global _start" in result

    def test_has_text_section(self):
        result = Compiler(_make_program()).compile()
        assert "section .text" in result

    def test_has_start_label(self):
        result = Compiler(_make_program()).compile()
        assert "_start:" in result

    def test_has_stack_frame_setup(self):
        result = Compiler(_make_program()).compile()
        assert "    push rbp" in result
        assert "    mov rbp, rsp" in result

    def test_prefix_order(self):
        result = Compiler(_make_program()).compile()
        lines = result.split("\n")
        assert lines[0] == "global _start"
        assert lines[1] == "section .text"
        assert lines[2] == "_start:"
        assert lines[3] == "    push rbp"
        assert lines[4] == "    mov rbp, rsp"


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
            "global _start",
            "section .text",
            "_start:",
            "    push rbp",
            "    mov rbp, rsp",
            "    mov rax, 60",
            "    mov rdi, 0",
            "    syscall",
            "",
            "",
        ])
        assert result == expected

    def test_single_exit(self):
        prog = _make_program(EXIT_STATEMENT(1, INT_EXPRESSION(1, 42)))
        result = Compiler(prog).compile()
        expected = "\n".join([
            "global _start",
            "section .text",
            "_start:",
            "    push rbp",
            "    mov rbp, rsp",
            "    push 42",
            "    pop rdi",
            "    mov rax, 60",
            "    syscall",
            "    mov rax, 60",
            "    mov rdi, 0",
            "    syscall",
            "",
            "",
        ])
        assert result == expected


class TestCompilerHelpers:
    def test_push(self):
        prog = _make_program()
        c = Compiler(prog)
        c._push("rax")
        assert "    push rax" in c._asm_output

    def test_pop(self):
        prog = _make_program()
        c = Compiler(prog)
        c._pop("rbx")
        assert "    pop rbx" in c._asm_output

    def test_add(self):
        c = Compiler(_make_program())
        c._add("rax", "rbx")
        assert "    add rax, rbx" in c._asm_output

    def test_imul(self):
        c = Compiler(_make_program())
        c._imul("rax", "rbx")
        assert "    imul rax, rbx" in c._asm_output

    def test_sub(self):
        c = Compiler(_make_program())
        c._sub("rax", "rbx")
        assert "    sub rax, rbx" in c._asm_output

    def test_idiv(self):
        c = Compiler(_make_program())
        c._idiv("rbx")
        assert "    idiv rbx" in c._asm_output

    def test_cqo(self):
        c = Compiler(_make_program())
        c._cqo()
        assert "    cqo" in c._asm_output


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


class TestCompilerLetStatement:
    def test_simple_let(self):
        prog = _make_program(
            LET_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 5))
        )
        result = Compiler(prog).compile()
        assert "    sub rsp, 8" in result
        assert "    push 5" in result
        assert "    pop rax" in result
        assert "    mov qword [rbp - 8], rax" in result

    def test_let_and_exit_with_var(self):
        prog = _make_program(
            LET_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 42)),
            EXIT_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "x")),
        )
        result = Compiler(prog).compile()
        assert "    mov qword [rbp - 8], rax" in result
        assert "    mov rax, qword [rbp - 8]" in result
        assert "    pop rdi" in result

    def test_two_vars_different_offsets(self):
        prog = _make_program(
            LET_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "a"), INT_EXPRESSION(1, 1)),
            LET_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "b"), INT_EXPRESSION(2, 2)),
        )
        result = Compiler(prog).compile()
        assert "    mov qword [rbp - 8], rax" in result
        assert "    mov qword [rbp - 16], rax" in result

    def test_duplicate_var_raises(self):
        prog = _make_program(
            LET_STATEMENT(1, IDENTIFIER_EXPRESSION(1, "x"), INT_EXPRESSION(1, 1)),
            LET_STATEMENT(2, IDENTIFIER_EXPRESSION(2, "x"), INT_EXPRESSION(2, 2)),
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
        assert "global _start" in result
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
        assert "global _start" in result
        assert "    mov rax, 60" in result

    def test_full_pipeline_arithmetic(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("exit 1 + 2;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    add rax, rbx" in result
        assert "    pop rdi" in result

    def test_full_pipeline_let_and_exit(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("let x = 42;\nexit x;").tokenize()
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

    def test_full_pipeline_let_with_expression(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("let a = 60 + 2 * 4;\nexit a;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "    imul rax, rbx" in result
        assert "    add rax, rbx" in result
        assert "    pop rdi" in result
