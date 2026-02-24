from parser.expressions import EXPRESSION, INT_EXPRESSION, STR_EXPRESSION
from parser.program import PROGRAM
from parser.statements import EXIT_STATEMENT, STATEMENT


class Compiler:
    def __init__(self, prog: PROGRAM) -> None:
        self._ast: PROGRAM = prog
        # self._statements: list[STATEMENT] = prog.statements
        # self._statements_len: int = len(self._statements)
        self._asm_output: list[str] = []
        # self._idx: int = 0

    # def _peek(self, offset: int = 0) -> STATEMENT | None:
    #     return self._statements[self._idx + offset] if self._idx + offset < self._statements_len else None
    #
    # def _consume(self) -> STATEMENT:
    #     self._idx += 1
    #     return self._statements[self._idx - 1]

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

    def _gen_exit(self, ret_code_expr: EXPRESSION) -> None:
        match ret_code_expr:
            case INT_EXPRESSION():
                self._mov("rax", "60")
                self._mov("rdi", str(ret_code_expr.val))
                self._syscall()

            case _:
                raise ValueError(f"unexpected expression '{ret_code_expr}' for 'exit' in line {ret_code_expr.line_number}")

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

