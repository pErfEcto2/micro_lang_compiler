# Tutorial

A guide on how to write code in the Micro language.

## Statements

Every statement must end with a semicolon (`;`).

### Variables

Declare variables with `int64`:

```
int64 x = 5;
int64 name = 10 + 20;
```

Variables can be used in expressions after they are declared:

```
int64 a = 60 + 2 * 4;
int64 b = a + 1;
```

### Constants

Declare constant (immutable) variables with `const`:

```
const int64 x = 5;
const int64 pi_approx = 3;
```

Constants cannot be reassigned:

```
const int64 x = 5;
x = 10;  // error: cant change constant 'x'
```

### Reassignment

Variables can be reassigned with `=`:

```
int64 x = 5;
x = 10;
x = x + 1;
```

### Print

Print an integer value to the console using `print`:

```
print 42;
int64 x = 10;
print x;
print x + 1;
```

### Exit

Exit the program with a return code using `exit`:

```
exit 0;
exit 42;
```

The return code can be any expression:

```
int64 x = 100;
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
int64 a = 2 + 3 * 4;
exit a;
```

This evaluates `3 * 4` first, then adds `2`, so the exit code is `14`.

### Variables in expressions

Variables can be used anywhere an integer literal can:

```
int64 a = 10;
int64 b = a + 5;
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
