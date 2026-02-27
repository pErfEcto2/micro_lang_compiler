from parser.expressions import BINARY_EXPRESSION, EXPRESSION, IDENTIFIER_EXPRESSION, INT_EXPRESSION
from parser.program import PROGRAM
from parser.statements import ASSIGN_STATEMENT, CONST_STATEMENT, EXIT_STATEMENT, INT64_STATEMENT, PRINT_STATEMENT, VARIABLE_TYPE
from tokenizer.keywords import INT_DIVISION_KEYWORD, MATH_OPERATION, MINUS_KEYWORD, MODULO_KEYWORD, MULTIPLY_KEYWORD, PLUS_KEYWORD


class Compiler:
    def __init__(self, prog: PROGRAM) -> None:
        self._ast: PROGRAM = prog
        self._text_s: list[str] = []
        self._data_s: set[str] = set()
        self._externs: set[str] = set()
        self._asm: list[str] = []
        self._vars: dict[str, int] = {}
        self._consts: dict[str, int] = {}
        self._num_of_vars: int = 0
        self._qword_size: int = 8

    def _get_stack_offset(self, var: str) -> int:
        assert var in self._vars or var in self._consts
        return self._qword_size * (self._vars.get(var) or self._consts.get(var))

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
                if expr.name not in self._vars and expr.name not in self._consts:
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
        if self._consts.get(identifier.name) is not None:
            raise ValueError(f"constant {identifier} already exists (line {identifier.line_number})")
        elif self._vars.get(identifier.name) is None:
            self._num_of_vars += 1
            self._vars[identifier.name] = self._num_of_vars
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

    def _gen_assing(self, identifier: IDENTIFIER_EXPRESSION, expr: EXPRESSION) -> None:
        if identifier.name in self._consts:
            raise ValueError(f"cant change constant '{identifier.name}' in line {identifier.line_number}")
        elif identifier.name not in self._vars:
            raise ValueError(f"unknown identifier '{identifier.name}' in line {identifier.line_number}")

        self._eval_expr(expr)
        self._pop("rax")
        stack_offset = self._get_stack_offset(identifier.name)
        self._mov(f"qword [rbp - {stack_offset}]", "rax")


    def _gen_const(self, var_statement: VARIABLE_TYPE) -> None:
        identifier = var_statement.identifier
        expr = var_statement.expr

        if self._vars.get(identifier.name) is not None:
            raise ValueError(f"variable {identifier} already exists (line {identifier.line_number})")
        elif self._consts.get(identifier.name) is None:
            self._num_of_vars += 1
            self._consts[identifier.name] = self._num_of_vars
        else:
            raise ValueError(f"constant {identifier} already exists (line {identifier.line_number})")

        stack_offset = self._get_stack_offset(identifier.name)
        self._sub("rsp", str(self._qword_size))
        self._eval_expr(expr)
        self._pop("rax")
        self._mov(f"qword [rbp - {stack_offset}]", "rax")

    def compile(self) -> str:
        for statement in self._ast.statements:
            match statement:
                case CONST_STATEMENT():
                    self._gen_const(statement.var_statement)

                case EXIT_STATEMENT():
                    self._gen_exit(statement.return_code)

                case INT64_STATEMENT():
                    self._gen_int64(statement.identifier, statement.expr)

                case PRINT_STATEMENT():
                    self._gen_print(statement.expr)

                case ASSIGN_STATEMENT():
                    self._gen_assing(statement.identifier, statement.expr)
                
                case _:
                    raise ValueError(f"unexpected statement '{statement}' in line {statement.line_number}")

        self._gen_suffix()
        self._gen_prefix()
        
        return "\n".join(self._asm) 

