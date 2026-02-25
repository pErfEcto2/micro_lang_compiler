from parser.expressions import BINARY_EXPRESSION, EXPRESSION, IDENTIFIER_EXPRESSION, INT_EXPRESSION
from parser.program import PROGRAM
from parser.statements import EXIT_STATEMENT, LET_STATEMENT
from tokenizer.keywords import INT_DIVISION_KEYWORD, MATH_OPERATION, MINUS_KEYWORD, MODULO_KEYWORD, MULTIPLY_KEYWORD, PLUS_KEYWORD


class Compiler:
    def __init__(self, prog: PROGRAM) -> None:
        self._ast: PROGRAM = prog
        self._asm_output: list[str] = []
        self._vars: dict[str, int] = {}
        self._num_of_vars: int = 0
        self._qword_size: int = 8

    def _get_stack_offset(self, var: str) -> int:
        assert var in self._vars
        return self._qword_size * self._vars[var]

    def _push(self, var: str) -> None:
        self._asm_output.append(f"    push {var}")

    def _mov(self, lval: str, rval: str) -> None:
        self._asm_output.append(f"    mov {lval}, {rval}")

    def _gen_prefix(self) -> None:
        self._asm_output.append("global _start")
        self._asm_output.append("section .text")
        self._asm_output.append("_start:")
        self._push("rbp")
        self._mov("rbp", "rsp")

    def _syscall(self) -> None:
        self._asm_output.append("    syscall")

    def _gen_suffix(self) -> None:
        self._mov("rax", "60")
        self._mov("rdi", "0")
        self._syscall()
        self._asm_output.append("\n")

    def _pop(self, var: str) -> None:
        self._asm_output.append(f"    pop {var}")

    def _add(self, lval: str, rval: str) -> None:
        self._asm_output.append(f"    add {lval}, {rval}")

    def _imul(self, lval: str, rval: str) -> None:
        self._asm_output.append(f"    imul {lval}, {rval}")

    def _idiv(self, divider: str) -> None:
        self._asm_output.append(f"    idiv {divider}")

    def _sub(self, lval: str, rval: str) -> None:
        self._asm_output.append(f"    sub {lval}, {rval}")

    def _cqo(self) -> None:
        self._asm_output.append("    cqo")

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
                if expr.name not in self._vars:
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

    def _gen_let(self, identifier: IDENTIFIER_EXPRESSION, expr: EXPRESSION) -> None:
        if self._vars.get(identifier.name) is None:
            self._num_of_vars += 1
            self._vars[identifier.name] = self._num_of_vars
        else:
            raise ValueError(f"identifier {identifier} already exists (line {identifier.line_number})")

        stack_offset = self._get_stack_offset(identifier.name)
        self._sub("rsp", str(self._qword_size))
        self._eval_expr(expr)
        self._pop("rax")
        self._mov(f"qword [rbp - {stack_offset}]", "rax")

    def compile(self) -> str:
        self._gen_prefix()

        for statement in self._ast.statements:
            match statement:
                case EXIT_STATEMENT():
                    self._gen_exit(statement.return_code)

                case LET_STATEMENT():
                    self._gen_let(statement.identifier, statement.expr)
                
                case _:
                    raise ValueError(f"unexpected statement '{statement}' in line {statement.line_number}")

        self._gen_suffix()
        
        return "\n".join(self._asm_output) 

