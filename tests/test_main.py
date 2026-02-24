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
                assert "global _start" in content
                assert "mov rdi, 69" in content
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
                assert "_start:" in content
                assert "mov rdi, 42" in content
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
    def test_prints_compiled_code_to_stdout(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("exit 1;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert "global _start" in result.stdout
                assert "mov rdi, 1" in result.stdout
        finally:
            os.unlink(src_path)

    def test_multiple_exits_in_output(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mil", delete=False) as f:
            f.write("exit 10;\nexit 20;")
            src_path = f.name

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "test_out")
                result = run_compiler("-n", "-o", out_path, src_path)
                assert "mov rdi, 10" in result.stdout
                assert "mov rdi, 20" in result.stdout
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
