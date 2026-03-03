from parser.expressions import BINARY_EXPRESSION, EXPRESSION, IDENTIFIER_EXPRESSION, INT_EXPRESSION
from parser.program import PROGRAM
from parser.statements import ASSIGN_STATEMENT, CLOSE_C_STATEMENT, CONST_STATEMENT, EXIT_STATEMENT, IF_STATEMENT, INT64_STATEMENT, OPEN_C_STATEMENT, PRINT_STATEMENT, STATEMENT, VARIABLE_TYPE
from tokenizer.keywords import INT_DIVISION_KEYWORD, MATH_OPERATION, MINUS_KEYWORD, MODULO_KEYWORD, MULTIPLY_KEYWORD, PLUS_KEYWORD


class Scope:
    def __init__(self, line_number: int, stack_offset: int = 0) -> None:
        self._vars: dict[str, int] = {}
        self._consts: dict[str, int] = {}
        self._size: int = 0
        self._stack_offset: int = stack_offset
        self.line_number: int = line_number

    def add_var(self, var_name: str) -> None:
        self._size += 1
        self._vars[var_name] = self._size + self._stack_offset

    def add_const(self, const_name: str) -> None:
        self._size += 1
        self._consts[const_name] = self._size + self._stack_offset

    def has_var(self, name: str) -> bool:
        return name in self._vars

    def has_const(self, name: str) -> bool:
        return name in self._consts

    def has(self, name: str) -> bool:
        return self.has_var(name) or self.has_const(name)

    def get(self, name: str) -> int:
        if name in self._vars:
            return self._vars[name]
        return self._consts[name]

    def get_size(self) -> int:
        return self._size

    def get_stack_offset(self) -> int:
        return self._size + self._stack_offset

class Compiler:
    def __init__(self, prog: PROGRAM) -> None:
        self._ast: PROGRAM = prog
        self._text_s: list[str] = []
        self._data_s: set[str] = set()
        self._externs: set[str] = set()
        self._asm: list[str] = []
        self._scopes: list[Scope] = [Scope(0)]
        self._qword_size: int = 8
        self._label_count: int = 0

    def _gen_label(self) -> int:
        self._label_count += 1
        return self._label_count - 1

    def _add_const(self, name: str) -> None:
        self._scopes[-1].add_const(name)

    def _add_var(self, name: str) -> None:
        self._scopes[-1].add_var(name)

    def _get_stack_offset(self, name: str) -> int:
        for scope in reversed(self._scopes):
            if scope.has(name):
                return self._qword_size * scope.get(name)

        raise ValueError(f"unknown identifier '{name}'")

    def _has_var_or_const(self, name: str) -> bool:
        for scope in self._scopes:
            if scope.has(name):
                return True
        return False

    def _push(self, var: str) -> None:
        self._text_s.append(f"    push {var}")

    def _mov(self, lval: str, rval: str) -> None:
        self._text_s.append(f"    mov {lval}, {rval}")

    def _gen_text_prefix(self) -> None:
        self._asm.append("section .text")
        self._asm.append("global main")
        self._asm.append("main:")
        self._asm.append("    push rbp")
        self._asm.append("    mov rbp, rsp")

    def _gen_externs(self) -> None:
        for ex in self._externs:
            self._asm.append(f"extern {ex}")

    def _gen_data_s(self) -> None:
        self._asm.append("section .data")
        self._asm.append("    int_fmt_str db \"%d\", 10, 0")

    def _gen_text_s(self) -> None:
        for text in self._text_s:
            self._asm.append(text)

    def _gen_prefix(self) -> None:
        self._gen_externs()
        self._gen_data_s()
        self._gen_text_prefix()
        self._gen_text_s()

    def _syscall(self) -> None:
        self._text_s.append("    syscall")

    def _gen_suffix(self) -> None:
        self._mov("rax", "60")
        self._mov("rdi", "0")
        self._syscall()

    def _pop(self, var: str) -> None:
        self._text_s.append(f"    pop {var}")

    def _add(self, lval: str, rval: str) -> None:
        self._text_s.append(f"    add {lval}, {rval}")

    def _imul(self, lval: str, rval: str) -> None:
        self._text_s.append(f"    imul {lval}, {rval}")

    def _idiv(self, divider: str) -> None:
        self._text_s.append(f"    idiv {divider}")

    def _sub(self, lval: str, rval: str) -> None:
        self._text_s.append(f"    sub {lval}, {rval}")

    def _lea(self, lval: str, rval: str) -> None:
        self._text_s.append(f"    lea {lval}, {rval}")

    def _cqo(self) -> None:
        self._text_s.append("    cqo")

    def _call(self, f: str) -> None:
        self._text_s.append(f"    call {f}")

    def _cmp(self, lval: str, rval: str) -> None:
        self._text_s.append(f"    cmp {lval}, {rval}")

    def _je(self, label: str) -> None:
        self._text_s.append(f"    je {label}")

    def _jmp(self, label: str) -> None:
        self._text_s.append(f"    jmp {label}")

    def _label(self, label: str) -> None:
        self._text_s.append(f"{label}:")

    def _eval_expr(self, expr: EXPRESSION) -> None:
        match expr:
            case INT_EXPRESSION():
                self._push(str(expr.val))
            case BINARY_EXPRESSION():
                self._eval_expr(expr.rval)
                self._eval_expr(expr.lval)
                self._pop("rax")
                self._pop("rbx")
                match expr.op:
                    case PLUS_KEYWORD():
                        self._add("rax", "rbx")
                        self._push("rax")
                    case MINUS_KEYWORD():
                        self._sub("rax", "rbx")
                        self._push("rax")
                    case MULTIPLY_KEYWORD():
                        self._imul("rax", "rbx")
                        self._push("rax")
                    case MODULO_KEYWORD():
                        self._cqo()
                        self._idiv("rbx")
                        self._push("rdx")
                    case INT_DIVISION_KEYWORD():
                        self._cqo()
                        self._idiv("rbx")
                        self._push("rax")
                    case _:
                        raise ValueError(f"invalid operation type '{type(expr.op)}' ('{MATH_OPERATION}' expected)")
            case IDENTIFIER_EXPRESSION():
                if not self._has_var_or_const(expr.name):
                    raise ValueError(f"unknown identifier '{expr.name}' in line {expr.line_number}")

                stack_offset = self._get_stack_offset(expr.name)
                self._mov("rax", f"qword [rbp - {stack_offset}]")
                self._push("rax")

            case _:
                raise ValueError(f"unexpected expression '{expr}' for 'exit' in line {expr.line_number}")

        return

    def _gen_exit(self, ret_code_expr: EXPRESSION) -> None:
        self._eval_expr(ret_code_expr)
        self._pop("rdi")
        self._mov("rax", "60")
        self._syscall()

    def _gen_int64(self, identifier: IDENTIFIER_EXPRESSION, expr: EXPRESSION) -> None:
        current_scope = self._scopes[-1]
        if current_scope.has_const(identifier.name):
            raise ValueError(f"constant {identifier} already exists (line {identifier.line_number})")
        elif not current_scope.has_var(identifier.name):
            self._add_var(identifier.name)
        else:
            raise ValueError(f"identifier {identifier} already exists (line {identifier.line_number})")

        stack_offset = self._get_stack_offset(identifier.name)
        self._sub("rsp", str(self._qword_size))
        self._eval_expr(expr)
        self._pop("rax")
        self._mov(f"qword [rbp - {stack_offset}]", "rax")

    def _gen_print(self, expr: EXPRESSION) -> None:
        self._externs.add("printf")
        self._eval_expr(expr)
        self._pop("rsi")
        self._lea("rdi", "[int_fmt_str]")
        self._mov("rax", "0")
        self._call("printf")

    def _gen_assign(self, identifier: IDENTIFIER_EXPRESSION, expr: EXPRESSION) -> None:
        for scope in reversed(self._scopes):
            if scope.has_const(identifier.name):
                raise ValueError(f"cant change constant '{identifier.name}' in line {identifier.line_number}")

            if scope.has_var(identifier.name):
                break
        else:
            raise ValueError(f"unknown identifier '{identifier.name}' in line {identifier.line_number}")

        self._eval_expr(expr)
        self._pop("rax")
        stack_offset = self._get_stack_offset(identifier.name)
        self._mov(f"qword [rbp - {stack_offset}]", "rax")

    def _gen_const(self, var_statement: VARIABLE_TYPE) -> None:
        identifier = var_statement.identifier
        expr = var_statement.expr
        current_scope = self._scopes[-1]

        if current_scope.has_var(identifier.name):
            raise ValueError(f"identifier {identifier} already exists (line {identifier.line_number})")
        elif not current_scope.has_const(identifier.name):
            self._add_const(identifier.name)
        else:
            raise ValueError(f"constant {identifier} already exists (line {identifier.line_number})")

        stack_offset = self._get_stack_offset(identifier.name)
        self._sub("rsp", str(self._qword_size))
        self._eval_expr(expr)
        self._pop("rax")
        self._mov(f"qword [rbp - {stack_offset}]", "rax")

    def _add_scope(self, line_number: int) -> None:
        stack_offset = self._scopes[-1].get_stack_offset()
        self._scopes.append(Scope(line_number, stack_offset))

    def _remove_scope(self) -> None:
        scope = self._scopes.pop()
        self._add("rsp", str(scope.get_size() * self._qword_size))

    def _gen_if(self, expr: EXPRESSION, true_body: list[STATEMENT], false_body: list[STATEMENT] | None = None) -> None:
        label_id = self._gen_label()
        else_label = f".else_{label_id}"
        end_label = f".end_{label_id}"

        self._eval_expr(expr)

        self._pop("rax")
        self._cmp("rax", "0")
        if false_body is None:
            self._je(end_label)
        else:
            self._je(else_label)
        
        for statement in true_body:
            self._compile_statement(statement)

        if false_body is not None:
            self._jmp(end_label)
            self._label(else_label)
            for statement in false_body:
                self._compile_statement(statement)
        self._label(end_label)

    def _compile_statement(self, statement) -> None:
        match statement:
            case IF_STATEMENT():
                self._gen_if(statement.expr, statement.true_body, statement.false_body)
            case OPEN_C_STATEMENT():
                self._add_scope(statement.line_number)
            case CLOSE_C_STATEMENT():
                self._remove_scope()
            case CONST_STATEMENT():
                self._gen_const(statement.var_statement)
            case EXIT_STATEMENT():
                self._gen_exit(statement.return_code)
            case INT64_STATEMENT():
                self._gen_int64(statement.identifier, statement.expr)
            case PRINT_STATEMENT():
                self._gen_print(statement.expr)
            case ASSIGN_STATEMENT():
                self._gen_assign(statement.identifier, statement.expr)
            case _:
                raise ValueError(f"unexpected statement '{statement}' in line {statement.line_number}")

    def compile(self) -> str:
        for statement in self._ast.statements:
            self._compile_statement(statement)

        if len(self._scopes) > 1:
            raise ValueError(f"scope was opened in line {self._scopes[-1].line_number}, but never closed")

        self._gen_suffix()
        self._gen_prefix()
        
        return "\n".join(self._asm) 

