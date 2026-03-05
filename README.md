# Micro Lang Compiler

A compiler for a minimal programming language that compiles to x86 assembly (NASM) and links with `gcc`.

## Language Features

- `int64` — declare Int64 variables
- `const` — declare constant (immutable) variables
- `=` — reassign variables
- `{ }` — scoped blocks with local variables
- `print` — print Int64 to console
- `exit` — exit with a return code
- Arithmetic expressions: `+`, `-`, `*`, `//`, `%`
- `if/else` — conditional branching
- `while` — loops
- Comparison: `>`, `<`, `>=`, `<=`, `==`, `!=`
- Comments: `# single-line`, `/* multi-line */`

## Pipeline

```
Source (.mil) → Tokenizer → Parser → Compiler → NASM → gcc → Executable
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
# compute and print a value
int64 x = 10 + 2 * 4;
x = x + 1;
print x;

const int64 y = 42;
print y;

if (x == y) {
  print 1;
} else {
  print 0;
}

{
  int64 x = 99;
  print x;
}

print x;

/* loop from 0 to 4 */
int64 i = 0;
while (i != 5) {
  print i;
  i = i + 1;
}

exit 0;
```

## Development

Requires Python >= 3.12. Uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
uv sync
uv run pytest
```
