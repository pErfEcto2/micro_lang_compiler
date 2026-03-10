import os
import subprocess
import tempfile
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_PATH = os.path.join(PROJECT_ROOT, "src", "main.py")


def run_compiler(*args, cwd=None):
    return subprocess.run(
        ["uv", "run", "python", MAIN_PATH, *args],
        capture_output=True,
        text=True,
        cwd=cwd or PROJECT_ROOT,
    )


class TestMainArgParsing:
    def test_no_arguments_fails(self):
        result = run_compiler()
        assert result.returncode != 0

    def test_help_flag(self):
        result = run_compiler("--help")
        assert result.returncode == 0
        assert "source code" in result.stdout.lower() or "src" in result.stdout


class TestMainFileNotFound:
    def test_nonexistent_file(self):
        result = run_compiler("nonexistent.mil")
        assert result.returncode == 1
        assert "no such file or directory" in result.stdout

    def test_nonexistent_path(self):
        result = run_compiler("/tmp/does/not/exist.mil")
        assert result.returncode == 1
        assert "no such file or directory" in result.stdout


class TestMainNoNasm:
    def test_creates_asm_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("exit 69;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                asm_path = out_path + ".asm"
                assert os.path.exists(asm_path)
                with open(asm_path) as f:
                    content = f.read()
                assert "global main" in content
                assert "push 69" in content
                assert "pop rdi" in content
        finally:
            os.unlink(src_path)

    def test_prints_created_message(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("exit 0;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                assert "created:" in result.stdout
        finally:
            os.unlink(src_path)

    def test_asm_contains_full_program(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("exit 42;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                run_compiler("-n", "-o", out_path, src_path)
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert "section .text" in content
                assert "main:" in content
                assert "push 42" in content
                assert "pop rdi" in content
                assert "syscall" in content
        finally:
            os.unlink(src_path)


class TestMainDefaultOutput:
    def test_default_output_is_a_out(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("exit 0;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                result = run_compiler("-n", src_path, cwd=tmpdir)
                assert result.returncode == 0
                assert os.path.exists(os.path.join(tmpdir, "a.out.asm"))
        finally:
            os.unlink(src_path)


class TestMainCompiledOutput:
    def test_verbose_prints_compiled_code_to_stdout(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("exit 1;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-v", "-o", out_path, src_path)
                assert "global main" in result.stdout
                assert "push 1" in result.stdout
        finally:
            os.unlink(src_path)

    def test_no_asm_on_stdout_without_verbose(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("exit 1;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert "global main" not in result.stdout
        finally:
            os.unlink(src_path)

    def test_verbose_multiple_exits_in_output(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("exit 10;\nexit 20;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-v", "-o", out_path, src_path)
                assert "push 10" in result.stdout
                assert "push 20" in result.stdout
        finally:
            os.unlink(src_path)


class TestMainInt64Statement:
    def test_int64_and_exit_creates_asm(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("int64 x = 42;\nexit x;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert "qword [rbp - 8]" in content
                assert "pop rdi" in content
        finally:
            os.unlink(src_path)

    def test_int64_with_arithmetic(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("int64 a = 1 + 2;\nexit a;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert "add rax, rbx" in content
        finally:
            os.unlink(src_path)

    def test_verbose_int64_shows_asm(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("int64 x = 5;\nexit x;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-v", "-o", out_path, src_path)
                assert "qword [rbp - 8]" in result.stdout
        finally:
            os.unlink(src_path)


class TestMainSourceErrors:
    def test_invalid_token_fails(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("@@@")
            src_path = f.name

        try:
            result = run_compiler("-n", src_path)
            assert result.returncode != 0
        finally:
            os.unlink(src_path)

    def test_parser_error_fails(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("foo;")
            src_path = f.name

        try:
            result = run_compiler("-n", src_path)
            assert result.returncode != 0
        finally:
            os.unlink(src_path)

    def test_empty_source_succeeds(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
        finally:
            os.unlink(src_path)


class TestMainPrintStatement:
    def test_print_creates_asm(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("print 42;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert "extern printf" in content
                assert "call printf" in content
        finally:
            os.unlink(src_path)

    def test_verbose_print_shows_asm(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("print 42;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-v", "-o", out_path, src_path)
                assert "call printf" in result.stdout
        finally:
            os.unlink(src_path)


class TestMainConstStatement:
    def test_const_creates_asm(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("const int64 x = 42;\nexit x;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert "qword [rbp - 8]" in content
        finally:
            os.unlink(src_path)

    def test_const_reassign_fails(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("const int64 x = 1;\nx = 10;")
            src_path = f.name

        try:
            result = run_compiler("-n", src_path)
            assert result.returncode != 0
        finally:
            os.unlink(src_path)


class TestMainAssignStatement:
    def test_assign_creates_asm(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("int64 x = 1;\nx = 10;\nexit x;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert "qword [rbp - 8]" in content
        finally:
            os.unlink(src_path)


class TestMainScopeStatement:
    def test_scope_creates_asm(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("int64 a = 1;\n{ int64 b = 2;\nprint b; }\nprint a;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert "add rsp, 8" in content
        finally:
            os.unlink(src_path)

    def test_unmatched_brackets_fails(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("{ int64 x = 1;")
            src_path = f.name

        try:
            result = run_compiler("-n", src_path)
            assert result.returncode != 0
        finally:
            os.unlink(src_path)

    def test_scope_with_shadowing(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("int64 a = 60;\n{ int64 a = 1;\nprint a; }\nprint a;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert "qword [rbp - 8]" in content
                assert "qword [rbp - 16]" in content
        finally:
            os.unlink(src_path)


class TestMainIfStatement:
    def test_simple_if_creates_asm(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("if (1) { print 42; }")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert "cmp rax, 0" in content
                assert "je .if_end_0" in content
                assert "call printf" in content
        finally:
            os.unlink(src_path)

    def test_if_else_creates_asm(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("if (0) { print 1; } else { print 2; }")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert "je .else_0" in content
                assert "jmp .if_end_0" in content
                assert ".else_0:" in content
                assert ".if_end_0:" in content
        finally:
            os.unlink(src_path)

    def test_if_with_var_condition(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("int64 x = 1;\nif (x) { print 42; }")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert "cmp rax, 0" in content
                assert "call printf" in content
        finally:
            os.unlink(src_path)

    def test_nested_if_else(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("if (1) { if (0) { print 1; } else { print 2; } } else { print 3; }")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert ".else_0:" in content
                assert ".if_end_0:" in content
                assert ".else_1:" in content
                assert ".if_end_1:" in content
        finally:
            os.unlink(src_path)

    def test_if_with_var_declaration_inside(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("if (1) { int64 x = 42; print x; }")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert "sub rsp, 8" in content
                assert "add rsp, 8" in content
        finally:
            os.unlink(src_path)

    def test_verbose_if_shows_asm(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("if (1) { print 1; }")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-v", "-o", out_path, src_path)
                assert "cmp rax, 0" in result.stdout
                assert ".if_end_0:" in result.stdout
        finally:
            os.unlink(src_path)

    def test_if_with_assign_in_body(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("int64 x = 0;\nif (1) { x = 42; }\nprint x;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
        finally:
            os.unlink(src_path)

    def test_multiple_sequential_ifs(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("if (1) { print 1; }\nif (1) { print 2; }\nif (0) { print 3; }")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert ".if_end_0:" in content
                assert ".if_end_1:" in content
                assert ".if_end_2:" in content
        finally:
            os.unlink(src_path)

    def test_if_with_expression_condition(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("if (1 + 2) { print 99; }")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert "add rax, rbx" in content
                assert "cmp rax, 0" in content
        finally:
            os.unlink(src_path)

    def test_if_else_with_exit(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("if (1) { exit 0; } else { exit 1; }")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
        finally:
            os.unlink(src_path)


def run_executable(src_code, *extra_compiler_args):
    """Helper: compile a .mil program to an executable, run it, return CompletedProcess."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
        f.write(src_code)
        src_path = f.name

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "test_out")
            comp = run_compiler("-o", out_path, *extra_compiler_args, src_path)
            if comp.returncode != 0:
                raise RuntimeError(f"compilation failed: {comp.stderr or comp.stdout}")
            return subprocess.run(
                [out_path],
                capture_output=True,
                text=True,
                timeout=10,
            )
    finally:
        os.unlink(src_path)


class TestRuntimeSubtractionAssociativity:
    def test_chained_subtraction_is_left_associative(self):
        """10 - 3 - 2 should be (10-3)-2 = 5, not 10-(3-2) = 9"""
        result = run_executable("exit 10 - 3 - 2;")
        assert result.returncode == 5

    def test_chained_addition_result(self):
        """1 + 2 + 3 should be 6 regardless of associativity"""
        result = run_executable("exit 1 + 2 + 3;")
        assert result.returncode == 6

    def test_chained_subtraction_four_operands(self):
        """20 - 5 - 3 - 2 should be ((20-5)-3)-2 = 10"""
        result = run_executable("exit 20 - 5 - 3 - 2;")
        assert result.returncode == 10

class TestRuntimeTokenizerStopChars:
    def test_modulo_without_spaces(self):
        """x%3 should tokenize as x, %, 3 — not as identifier 'x%3'"""
        result = run_executable("int64 x = 10;\nexit x%3;")
        assert result.returncode == 1

    def test_int_division_without_spaces(self):
        """x//3 should tokenize as x, //, 3 — not as identifier 'x//3'"""
        result = run_executable("int64 x = 10;\nexit x//3;")
        assert result.returncode == 3


class TestRuntimeWhileScope:
    def test_while_with_var_does_not_crash(self):
        """While loop declaring a variable should not segfault from stack leak"""
        src = "int64 x = 0;\nwhile (x < 100) {\n  int64 y = x;\n  x = x + 1;\n}\nexit x % 256;"
        result = run_executable(src)
        assert result.returncode == 100

    def test_while_large_loop_does_not_segfault(self):
        """A long-running while loop with var decl must not overflow the stack"""
        src = "int64 x = 0;\nwhile (x < 2000000) {\n  int64 y = x;\n  x = x + 1;\n}\nexit 42;"
        result = run_executable(src)
        assert result.returncode == 42


class TestMainPostfixStatement:
    def test_postfix_increment_creates_asm(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("int64 x = 0;\nx++;\nexit x;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert "inc qword [rbp - 8]" in content
        finally:
            os.unlink(src_path)

    def test_postfix_decrement_creates_asm(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("int64 x = 5;\nx--;\nexit x;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert "dec qword [rbp - 8]" in content
        finally:
            os.unlink(src_path)

    def test_const_postfix_fails(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("const int64 x = 5;\nx++;")
            src_path = f.name

        try:
            result = run_compiler("-n", src_path)
            assert result.returncode != 0
        finally:
            os.unlink(src_path)


class TestMainPrefixStatement:
    def test_prefix_increment_creates_asm(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("int64 x = 0;\n++x;\nexit x;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert "inc qword [rbp - 8]" in content
        finally:
            os.unlink(src_path)

    def test_prefix_decrement_creates_asm(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("int64 x = 5;\n--x;\nexit x;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert result.returncode == 0
                with open(out_path + ".asm") as f:
                    content = f.read()
                assert "dec qword [rbp - 8]" in content
        finally:
            os.unlink(src_path)


class TestRuntimePostfixIncrement:
    def test_postfix_increment(self):
        result = run_executable("int64 x = 0;\nx++;\nexit x;")
        assert result.returncode == 1

    def test_postfix_decrement(self):
        result = run_executable("int64 x = 5;\nx--;\nexit x;")
        assert result.returncode == 4

    def test_postfix_in_while_loop(self):
        src = "int64 i = 0;\nwhile (i < 10) {\n  i++;\n}\nexit i % 256;"
        result = run_executable(src)
        assert result.returncode == 10

    def test_postfix_decrement_in_while_loop(self):
        src = "int64 i = 5;\nwhile (i > 0) {\n  i--;\n}\nexit i;"
        result = run_executable(src)
        assert result.returncode == 0

    def test_postfix_expr_returns_old_value(self):
        src = "int64 x = 5;\nint64 a = x++;\nexit a;"
        result = run_executable(src)
        assert result.returncode == 5

    def test_postfix_expr_mutates_variable(self):
        src = "int64 x = 5;\nint64 a = x++;\nexit x;"
        result = run_executable(src)
        assert result.returncode == 6

    def test_postfix_decrement_expr_returns_old_value(self):
        src = "int64 x = 5;\nint64 a = x--;\nexit a;"
        result = run_executable(src)
        assert result.returncode == 5

    def test_postfix_decrement_expr_mutates_variable(self):
        src = "int64 x = 5;\nint64 a = x--;\nexit x;"
        result = run_executable(src)
        assert result.returncode == 4


class TestRuntimePrefixIncrement:
    def test_prefix_increment(self):
        result = run_executable("int64 x = 0;\n++x;\nexit x;")
        assert result.returncode == 1

    def test_prefix_decrement(self):
        result = run_executable("int64 x = 5;\n--x;\nexit x;")
        assert result.returncode == 4

    def test_prefix_expr_returns_new_value(self):
        src = "int64 x = 5;\nint64 a = ++x;\nexit a;"
        result = run_executable(src)
        assert result.returncode == 6

    def test_prefix_decrement_expr_returns_new_value(self):
        src = "int64 x = 5;\nint64 a = --x;\nexit a;"
        result = run_executable(src)
        assert result.returncode == 4

    def test_prefix_in_while_condition(self):
        src = "int64 i = 0;\nwhile (++i < 5) {\n  print i;\n}\nexit i;"
        result = run_executable(src)
        assert result.returncode == 5
