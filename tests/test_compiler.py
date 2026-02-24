import pytest
from compiler.compiler import Compiler
from parser.program import PROGRAM
from parser.statements import EXIT_STATEMENT, STATEMENT
from parser.expressions import INT_EXPRESSION, STR_EXPRESSION


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

    def test_prefix_order(self):
        result = Compiler(_make_program()).compile()
        lines = result.split("\n")
        assert lines[0] == "global _start"
        assert lines[1] == "section .text"
        assert lines[2] == "_start:"


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
        assert "    mov rax, 60" in result
        assert "    mov rdi, 69" in result
        assert "    syscall" in result

    def test_exit_with_zero(self):
        prog = _make_program(EXIT_STATEMENT(1, INT_EXPRESSION(1, 0)))
        result = Compiler(prog).compile()
        assert "    mov rdi, 0" in result

    def test_exit_with_large_int(self):
        prog = _make_program(EXIT_STATEMENT(1, INT_EXPRESSION(1, 255)))
        result = Compiler(prog).compile()
        assert "    mov rdi, 255" in result

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
        assert "    mov rdi, 1" in result
        assert "    mov rdi, 2" in result

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
            "    mov rax, 60",
            "    mov rdi, 42",
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


class TestCompilerErrors:
    def test_unexpected_statement_type(self):
        prog = _make_program(STATEMENT(1))
        with pytest.raises(ValueError, match="unexpected statement"):
            Compiler(prog).compile()

    def test_unexpected_statement_reports_line(self):
        prog = _make_program(STATEMENT(7))
        with pytest.raises(ValueError, match="line 7"):
            Compiler(prog).compile()


class TestCompilerIntegration:
    def test_full_pipeline_exit(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("exit 69;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "global _start" in result
        assert "mov rdi, 69" in result
        assert "syscall" in result

    def test_full_pipeline_multiple_exits(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("exit 69;\nexit 70;").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "mov rdi, 69" in result
        assert "mov rdi, 70" in result

    def test_full_pipeline_empty(self):
        from tokenizer.tokenizer import Tokenizer
        from parser.parser import Parser

        tokens = Tokenizer("").tokenize()
        prog = Parser(tokens).parse()
        result = Compiler(prog).compile()
        assert "global _start" in result
        assert "    mov rax, 60" in result
