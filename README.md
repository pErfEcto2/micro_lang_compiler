# Micro Lang Compiler

A compiler for a minimal programming language that compiles to x86 assembly (NASM) and links with `ld`.

## Language Features

- `let` — declare Int32 variables
- `print` — print Int32 to console
- `if/else` — branching
- `while` — loops
- `exit` — exit with a return code
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `>`, `<`, `>=`, `<=`, `==`, `!=`

## Pipeline

```
Source (.mil) → Tokenizer → Parser → Compiler → NASM → ld → Executable
```

## Usage

```bash
python src/main.py <source.mil>
python src/main.py -o output <source.mil>
python src/main.py -n <source.mil>   # stop after compiling (skip nasm)
python src/main.py -l <source.mil>   # stop after nasm (skip linker)
```

## Development

Requires Python >= 3.12. Uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
uv sync
uv run pytest
```
