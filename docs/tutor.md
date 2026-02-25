# Tutorial

A guide on how to write code in the Micro language.

## Statements

Every statement must end with a semicolon (`;`).

### Variables

Declare variables with `let`:

```
let x = 5;
let name = 10 + 20;
```

Variables can be used in expressions after they are declared:

```
let a = 60 + 2 * 4;
let b = a + 1;
```

### Exit

Exit the program with a return code using `exit`:

```
exit 0;
exit 42;
```

The return code can be any expression:

```
let x = 100;
exit x - 50;
```

## Expressions

### Integer literals

Plain integer values:

```
exit 42;
```

### Arithmetic

All five math operators are supported: `+`, `-`, `*`, `//`, `%`.

`*`, `//`, and `%` bind tighter than `+` and `-`:

```
let a = 2 + 3 * 4;
exit a;
```

This evaluates `3 * 4` first, then adds `2`, so the exit code is `14`.

### Variables in expressions

Variables can be used anywhere an integer literal can:

```
let a = 10;
let b = a + 5;
exit b;
```

## Compiling

```sh
uv run python src/main.py program.mil
```

### Compiler flags

| Flag | Description |
|------|-------------|
| `-o`, `--output` | Path to the output file (default: `a.out`) |
| `-n`, `--no-nasm` | Stop after compiling (produce `.asm` only) |
| `-l`, `--no-linker` | Stop after nasm (produce `.o` only) |
| `-v`, `--verbose` | Print source code, tokens, AST, and assembly |

### Example

```sh
uv run python src/main.py -n -v -o build/out program.mil
```
