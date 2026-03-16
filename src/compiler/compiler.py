from parser.expressions import BINARY_EXPRESSION, CHAR_EXPRESSION, EXPRESSION, IDENTIFIER_EXPRESSION, INT_EXPRESSION, POSTFIX_EXPRESSION, PREFIX_EXPRESSION
from parser.program import PROGRAM
from parser.statements import ASSIGN_STATEMENT, CHAR_STATEMENT, CLOSE_C_STATEMENT, CONST_STATEMENT, EXIT_STATEMENT, FOR_STATEMENT, IF_STATEMENT, INT64_STATEMENT, OPEN_C_STATEMENT, POSTFIX_STATEMENT, PREFIX_STATEMENT, PRINT_STATEMENT, STATEMENT, VARIABLE_TYPE, WHILE_STATEMENT
from tokenizer.keywords import DECREMENT_KEYWORD, EQUALS_KEYWORD, GREATER_KEYWORD, GREATER_OR_EQUALS_KEYWORD, INCREMENT_KEYWORD, INT_DIVISION_KEYWORD, LESS_KEYWORD, LESS_OR_EQUALS_KEYWORD, MATH_OPERATION, MINUS_KEYWORD, MODULO_KEYWORD, MULTIPLY_KEYWORD, NOT_EQUALS_KEYWORD, PLUS_KEYWORD, UNARY_MATH_OPERATION


class Scope:
    def __init__(self, line_number: int, stack_offset: int = 0) -> None:
        self._vars: dict[str, tuple[int, int]] = {}
        self._consts: dict[str, tuple[int, int]] = {}
        self._size: int = 0
        self._stack_offset: int = stack_offset
        self.line_number: int = line_number

    def add_var(self, var_name: str, var_size: int) -> None:
        self._size += 8
        self._vars[var_name] = (var_size, self._size + self._stack_offset)

    def add_const(self, const_name: str, const_size: int) -> None:
        self._size += 8
        self._consts[const_name] = (const_size, self._size + self._stack_offset)

    def has_var(self, name: str) -> bool:
        return name in self._vars

    def has_const(self, name: str) -> bool:
        return name in self._consts

    def has(self, name: str) -> bool:
        return self.has_var(name) or self.has_const(name)

    def get(self, name: str) -> tuple[int, int]:
        """
        returns: tuple[size, stack_offset]
        """
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
        self._label_count: int = 0

    def _gen_label(self) -> int:
        self._label_count += 1
        return self._label_count - 1

    def _add_const(self, name: str, const_size: int) -> None:
        self._scopes[-1].add_const(name, const_size)

    def _add_var(self, name: str, var_size: int) -> None:
        self._scopes[-1].add_var(name, var_size)

    def _get_stack_offset(self, name: str) -> tuple[int, int]:
        """
        returns: tuple[size, stack_offset]
        """
        for scope in reversed(self._scopes):
            if scope.has(name):
                return scope.get(name)

        raise ValueError(f"unknown identifier '{name}'")

    def _has_var_or_const(self, name: str) -> bool:
        for scope in self._scopes:
            if scope.has(name):
                return True
        return False

    def _has_var(self, name: str) -> bool:
        for scope in self._scopes:
            if scope.has_var(name):
                return True
        return False

    def _has_const(self, name: str) -> bool:
        for scope in self._scopes:
            if scope.has_const(name):
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
        for data in self._data_s:
            self._asm.append(f"    {data}")

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

    def _setg(self, var: str) -> None:
        self._text_s.append(f"    setg {var}")

    def _setge(self, var: str) -> None:
        self._text_s.append(f"    setge {var}")

    def _setl(self, var: str) -> None:
        self._text_s.append(f"    setl {var}")

    def _setle(self, var: str) -> None:
        self._text_s.append(f"    setle {var}")

    def _sete(self, var: str) -> None:
        self._text_s.append(f"    sete {var}")
    
    def _setne(self, var: str) -> None:
        self._text_s.append(f"    setne {var}")

    def _inc(self, var: str) -> None:
        self._text_s.append(f"    inc {var}")

    def _dec(self, var: str) -> None:
        self._text_s.append(f"    dec {var}")

    def _movzx(self, lval: str, rval: str) -> None:
        self._text_s.append(f"    movzx {lval}, {rval}")

    def _eval_expr(self, expr: EXPRESSION) -> None:
        match expr:
            case INT_EXPRESSION() | CHAR_EXPRESSION():
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
                    case GREATER_KEYWORD():
                        self._cmp("rax", "rbx")
                        self._setg("al")
                        self._movzx("rax", "al")
                        self._push("rax")
                    case GREATER_OR_EQUALS_KEYWORD():
                        self._cmp("rax", "rbx")
                        self._setge("al")
                        self._movzx("rax", "al")
                        self._push("rax")
                    case  LESS_KEYWORD():
                        self._cmp("rax", "rbx")
                        self._setl("al")
                        self._movzx("rax", "al")
                        self._push("rax")
                    case LESS_OR_EQUALS_KEYWORD():
                        self._cmp("rax", "rbx")
                        self._setle("al")
                        self._movzx("rax", "al")
                        self._push("rax")
                    case EQUALS_KEYWORD():
                        self._cmp("rax", "rbx")
                        self._sete("al")
                        self._movzx("rax", "al")
                        self._push("rax")
                    case NOT_EQUALS_KEYWORD():
                        self._cmp("rax", "rbx")
                        self._setne("al")
                        self._movzx("rax", "al")
                        self._push("rax")
                    case _:
                        raise ValueError(f"invalid operation type '{type(expr.op)}' ('{MATH_OPERATION}' expected)")
            case IDENTIFIER_EXPRESSION():

                if not self._has_var_or_const(expr.name):
                    raise ValueError(f"unknown identifier '{expr.name}' in line {expr.line_number}")

                size, stack_offset = self._get_stack_offset(expr.name)
                match size:
                    case 1:
                        self._movzx("rax", f"byte [rbp - {stack_offset}]")
                    case 8:
                        self._mov("rax", f"qword [rbp - {stack_offset}]")
                    case _:
                        raise ValueError(f"invalid expression size in line {expr.line_number}")

                self._push("rax")

            case POSTFIX_EXPRESSION():
                for scope in reversed(self._scopes):
                    if scope.has_const(expr.identifier.name):
                        raise ValueError(f"cant change constant '{expr.identifier.name}' in line {expr.identifier.line_number}")

                    if scope.has_var(expr.identifier.name):
                        break
                else:
                    raise ValueError(f"unknown identifier '{expr.identifier.name}' in line {expr.identifier.line_number}")

                size, stack_offset = self._get_stack_offset(expr.identifier.name)
                match size:
                    case 1:
                        var_size = "byte"
                        self._movzx("rax", f"{var_size} [rbp - {stack_offset}]")
                        self._push(f"rax")
                    case 8:
                        var_size = "qword"
                        self._push(f"{var_size} [rbp - {stack_offset}]")
                    case _:
                        raise ValueError(f"invalid postfix expression size in line {expr.line_number}")

                match expr.op:
                    case INCREMENT_KEYWORD():
                        self._inc(f"{var_size} [rbp - {stack_offset}]")
                    case DECREMENT_KEYWORD():
                        self._dec(f"{var_size} [rbp - {stack_offset}]")

            case PREFIX_EXPRESSION():
                for scope in reversed(self._scopes):
                    if scope.has_const(expr.identifier.name):
                        raise ValueError(f"cant change constant '{expr.identifier.name}' in line {expr.identifier.line_number}")

                    if scope.has_var(expr.identifier.name):
                        break
                else:
                    raise ValueError(f"unknown identifier '{expr.identifier.name}' in line {expr.identifier.line_number}")

                size, stack_offset = self._get_stack_offset(expr.identifier.name)
                match size:
                    case 1:
                        var_size = "byte"
                    case 8:
                        var_size = "qword"
                    case _:
                        raise ValueError(f"invalid postfix expression size in line {expr.line_number}")

                match expr.op:
                    case INCREMENT_KEYWORD():
                        self._inc(f"{var_size} [rbp - {stack_offset}]")
                    case DECREMENT_KEYWORD():
                        self._dec(f"{var_size} [rbp - {stack_offset}]")

                match size:
                    case 1:
                        self._movzx("rax", f"{var_size} [rbp - {stack_offset}]")
                        self._push(f"rax")
                    case 8:
                        self._push(f"{var_size} [rbp - {stack_offset}]")

            case _:
                raise ValueError(f"unexpected expression '{expr}' in line {expr.line_number}")

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
            self._add_var(identifier.name, 8)
        else:
            raise ValueError(f"identifier {identifier} already exists (line {identifier.line_number})")

        size, stack_offset = self._get_stack_offset(identifier.name)
        self._sub("rsp", "8")
        self._eval_expr(expr)
        self._pop("rax")
        self._mov(f"qword [rbp - {stack_offset}]", "rax")

    def _gen_print(self, expr: EXPRESSION) -> None:
        self._externs.add("printf")
        self._eval_expr(expr)

        match expr:
            case CHAR_EXPRESSION():
                fmt = "char_fmt_str"
                self._data_s.add(f"{fmt} db \"%c\", 0")
            case IDENTIFIER_EXPRESSION():
                size, _ = self._get_stack_offset(expr.name)
                match size:
                    case 1:
                        fmt = "char_fmt_str"
                        self._data_s.add(f"{fmt} db \"%c\", 0")
                    case 8:
                        fmt = "int64_fmt_str"
                        self._data_s.add(f"{fmt} db \"%lld\", 0")
                    case _:
                        raise ValueError(f"invalid expression size in line {expr.line_number}")
            case INT_EXPRESSION() | BINARY_EXPRESSION():
                fmt = "int64_fmt_str"
                self._data_s.add(f"{fmt} db \"%lld\", 0")
            case POSTFIX_EXPRESSION():
                size, _ = self._get_stack_offset(expr.identifier.name)
                match size:
                    case 1:
                        fmt = "char_fmt_str"
                        self._data_s.add(f"{fmt} db \"%c\", 0")
                    case 8:
                        fmt = "int64_fmt_str"
                        self._data_s.add(f"{fmt} db \"%lld\", 0")
                    case _:
                        raise ValueError(f"invalid expression size in line {expr.line_number}")
            case PREFIX_EXPRESSION():
                size, _ = self._get_stack_offset(expr.identifier.name)
                match size:
                    case 1:
                        fmt = "char_fmt_str"
                        self._data_s.add(f"{fmt} db \"%c\", 0")
                    case 8:
                        fmt = "int64_fmt_str"
                        self._data_s.add(f"{fmt} db \"%lld\", 0")
                    case _:
                        raise ValueError(f"invalid expression size in line {expr.line_number}")
            case _:
                raise ValueError(f"invalid expression in line {expr.line_number}")

        self._pop("rsi")
        self._lea("rdi", f"[{fmt}]")
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
        size, stack_offset = self._get_stack_offset(identifier.name)
        match size:
            case 1:
                register = "al"
                var_size = "byte"
            case 8:
                register = "rax"
                var_size = "qword"
            case _:
                raise ValueError(f"invalid variable size in line {identifier.line_number}")
        self._pop("rax")
        self._mov(f"{var_size} [rbp - {stack_offset}]", register)

    def _gen_const(self, var_statement: VARIABLE_TYPE) -> None:
        identifier = var_statement.identifier
        expr = var_statement.expr
        current_scope = self._scopes[-1]

        if current_scope.has_var(identifier.name):
            raise ValueError(f"identifier {identifier} already exists (line {identifier.line_number})")
        elif not current_scope.has_const(identifier.name):
            self._add_const(identifier.name, var_statement.size)
        else:
            raise ValueError(f"constant {identifier} already exists (line {identifier.line_number})")

        size, stack_offset = self._get_stack_offset(identifier.name)
        self._sub("rsp", "8")
        self._eval_expr(expr)
        match size:
            case 1:
                register = "al"
                var_size = "byte"
            case 8:
                register = "rax"
                var_size = "qword"
            case _:
                raise ValueError(f"invalid constant size in line {identifier.line_number}")
        self._pop("rax")
        self._mov(f"{var_size} [rbp - {stack_offset}]", register)

    def _add_scope(self, line_number: int) -> None:
        stack_offset = self._scopes[-1].get_stack_offset()
        self._scopes.append(Scope(line_number, stack_offset))

    def _remove_scope(self) -> None:
        scope = self._scopes.pop()
        if scope.get_size() > 0:
            self._add("rsp", str(scope.get_size()))

    def _gen_if(self, expr: EXPRESSION, true_body: list[STATEMENT], false_body: list[STATEMENT] | None = None) -> None:
        label_id = self._gen_label()
        else_label = f".else_{label_id}"
        end_label = f".if_end_{label_id}"

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

    def _gen_while(self, expr: EXPRESSION, body: list[STATEMENT]) ->  None:
        label_id = self._gen_label()
        start_label = f".while_start_{label_id}"
        end_label = f".while_end_{label_id}"

        self._label(start_label)
        self._eval_expr(expr)
        self._pop("rax")
        self._cmp("rax", "0")
        self._je(end_label)

        for statement in body:
            self._compile_statement(statement)

        self._jmp(start_label)

        self._label(end_label)

    def _gen_unary_op(self, identifier: IDENTIFIER_EXPRESSION, op: UNARY_MATH_OPERATION) -> None:
        for scope in reversed(self._scopes):
            if scope.has_const(identifier.name):
                raise ValueError(f"cant change constant '{identifier.name}' in line {identifier.line_number}")

            if scope.has_var(identifier.name):
                break
        else:
            raise ValueError(f"unknown identifier '{identifier.name}' in line {identifier.line_number}")

        size, stack_offset = self._get_stack_offset(identifier.name)
        match size:
            case 1:
                var_size = "byte"
            case 8:
                var_size = "qword"
            case _:
                raise ValueError(f"invalid expression size in line {identifier.line_number}")

        match op:
            case INCREMENT_KEYWORD():
                self._inc(f"{var_size} [rbp - {stack_offset}]")
            case DECREMENT_KEYWORD():
                self._dec(f"{var_size} [rbp - {stack_offset}]")
            case _:
                raise ValueError(f"unknown unary math operation '{op}' in line {op.line_number}")

    def _gen_for(self, ln: int, body: list[STATEMENT], init: STATEMENT | None, cond: EXPRESSION | None, inc: STATEMENT | None) -> None:
        label_id = self._gen_label()
        for_start = f".for_start_{label_id}"
        for_end = f".for_end_{label_id}"

        self._add_scope(ln)

        if init is not None:
            self._compile_statement(init)
        
        self._label(for_start)

        if cond is not None:
            self._eval_expr(cond)
            self._pop("rax")
            self._cmp("rax", "0")
            self._je(for_end)

        for statement in body:
            self._compile_statement(statement)

        if inc is not None:
            self._compile_statement(inc)

        self._jmp(for_start)

        self._label(for_end)

        self._remove_scope()

    def _gen_char(self, identifier: IDENTIFIER_EXPRESSION, expr: EXPRESSION) -> None:
        current_scope = self._scopes[-1]
        if current_scope.has_const(identifier.name):
            raise ValueError(f"constant {identifier} already exists (line {identifier.line_number})")
        elif not current_scope.has_var(identifier.name):
            self._add_var(identifier.name, 1)
        else:
            raise ValueError(f"identifier {identifier} already exists (line {identifier.line_number})")

        _, stack_offset = self._get_stack_offset(identifier.name)
        self._sub("rsp", "8")
        self._eval_expr(expr)
        self._pop("rax")
        self._mov(f"byte [rbp - {stack_offset}]", "al")

    def _compile_statement(self, statement) -> None:
        match statement:
            case CHAR_STATEMENT():
                self._gen_char(statement.identifier, statement.expr)
            case FOR_STATEMENT():
                self._gen_for(statement.line_number, statement.body, statement.initialization, statement.condition, statement.increment)
            case POSTFIX_STATEMENT() | PREFIX_STATEMENT():
                self._gen_unary_op(statement.identifier, statement.op)
            case WHILE_STATEMENT():
                self._gen_while(statement.expr, statement.body)
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

