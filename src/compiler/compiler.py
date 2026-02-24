from parser.expressions import BINARY_EXPRESSION, EXPRESSION, INT_EXPRESSION
from parser.program import PROGRAM
from parser.statements import EXIT_STATEMENT
from tokenizer.keywords import MATH_OPERATION, MULTIPLY_KEYWORD, PLUS_KEYWORD


class Compiler:
    def __init__(self, prog: PROGRAM) -> None:
        self._ast: PROGRAM = prog
        self._asm_output: list[str] = []

    def _gen_prefix(self) -> None:
        self._asm_output.append("global _start")
        self._asm_output.append("section .text")
        self._asm_output.append("_start:")

    def _mov(self, lval: str, rval: str) -> None:
        self._asm_output.append(f"    mov {lval}, {rval}")

    def _syscall(self) -> None:
        self._asm_output.append("    syscall")

    def _gen_suffix(self) -> None:
        self._mov("rax", "60")
        self._mov("rdi", "0")
        self._syscall()
        self._asm_output.append("\n")

    def _push(self, var: str) -> None:
        self._asm_output.append(f"    push {var}")

    def _pop(self, var: str) -> None:
        self._asm_output.append(f"    pop {var}")

    def _add(self, lval: str, rval: str) -> None:
        self._asm_output.append(f"    add {lval}, {rval}")

    def _mul(self, lval: str, rval: str) -> None:
        self._asm_output.append(f"    mul {lval}, {rval}")

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
                    case MULTIPLY_KEYWORD():
                        self._mul("rax", "rbx")
                        self._push("rax")
                    case _:
                        raise ValueError(f"invalid operation type '{type(expr.op)}' ('{type(MATH_OPERATION)}' expected)")
            case _:
                raise ValueError(f"unexpected expression '{expr}' for 'exit' in line {expr.line_number}")

        return

    def _gen_exit(self, ret_code_expr: EXPRESSION) -> None:
        self._eval_expr(ret_code_expr)
        self._pop("rdi")
        self._mov("rax", "60")
        self._syscall()

    def compile(self) -> str:
        self._gen_prefix()

        for statement in self._ast.statements:
            match statement:
                case EXIT_STATEMENT():
                    self._gen_exit(statement.return_code)
                
                case _:
                    raise ValueError(f"unexpected statement '{statement}' in line {statement.line_number}")

        self._gen_suffix()
        
        return "\n".join(self._asm_output) 

