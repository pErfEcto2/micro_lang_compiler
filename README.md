# Micro Lang Compiler

A compiler for a minimal programming language that compiles to x86 assembly (NASM) and links with `ld`.

## Language Features

- `exit` — exit with a return code
- Arithmetic expressions: `+`, `*` 
- `let` — declare Int32 variables *(planned)*
- `print` — print Int32 to console *(planned)*
- `if/else` — branching *(planned)*
- `while` — loops *(planned)*
- More arithmetic: `-`, `/`, `%` *(planned)*
- Comparison: `>`, `<`, `>=`, `<=`, `==`, `!=` *(planned)*

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
python src/main.py -v <source.mil>   # verbose: show tokens, AST and assembly
```

## Example

```
exit 10 + 2 * 4 + 1;
```

## Development

Requires Python >= 3.12. Uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
uv sync
uv run pytest
```
