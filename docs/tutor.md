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

### Scopes

Use curly brackets `{ }` to create a new scope. Variables declared inside a scope are local to it and cleaned up when the scope ends. Inner scopes can access variables from outer scopes, and can shadow them with new declarations:

```
int64 x = 10;
print x;

{
  print x;
  int64 x = 99;
  print x;
}

print x;
```

Output: `10`, `10`, `99`, `10`.

### If / Else

Use `if` for conditional branching. The condition must be in parentheses, and the body must be in curly brackets:

```
if (1) {
  print 42;
}
```

The condition is truthy if it is non-zero, and falsy if it is zero:

```
int64 x = 0;
if (x) {
  print 1;
}
```

This prints nothing because `x` is `0`.

Add an `else` block for the alternative branch:

```
int64 x = 0;
if (x) {
  print 1;
} else {
  print 2;
}
```

Output: `2`.

You can nest `if`/`else` statements:

```
int64 x = 0;
int64 y = 1;
if (x) {
  print 1;
} else {
  if (y) {
    print 2;
  } else {
    print 3;
  }
}
```

Output: `2`.

Variables declared inside an `if` or `else` block are scoped to that block:

```
int64 x = 1;
if (x) {
  int64 y = 42;
  print y;
}
```

The condition can be any expression:

```
int64 a = 3;
int64 b = 2;
if (a - b) {
  print 1;
}
```

Output: `1` (because `3 - 2 = 1`, which is non-zero).

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
