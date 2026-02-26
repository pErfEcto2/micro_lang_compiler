import argparse
import os
import subprocess
from compiler.compiler import Compiler
from tokenizer.tokenizer import Tokenizer
from parser.parser import Parser


parser = argparse.ArgumentParser()

parser.add_argument("-o", "--output", help="specify path to the output file", type=str)
parser.add_argument("-l", "--no-linker", help="dont use a linker, stop after nasm", action="store_true")
parser.add_argument("-n", "--no-nasm", help="dont use nasm, stop after compiling", action="store_true")
parser.add_argument("-v", "--verbose", help="show source code, tokens list, ast tree and compiled code", action="store_true")
parser.add_argument("src", help="path to the file with a source code")

args = parser.parse_args()

N = 50

if not os.path.exists(args.src):
    print(f"no such file or directory: {args.src}")
    exit(1)

with open(args.src, "r") as src_f:
    src_code = src_f.read()

if args.verbose:
    print("SOURCE CODE".center(N, "="))
    print(src_code)
    print()

tokenizer = Tokenizer(src_code)
tokens = tokenizer.tokenize()

if args.verbose:
    print("TOKENS".center(N, "="))
    print(tokens)
    print()

ast_parser = Parser(tokens)
ast_tree = ast_parser.parse()

if args.verbose:
    print("AST TREE".center(N, "="))
    print(ast_tree)
    print()

compiler = Compiler(ast_tree)
compiled_code = compiler.compile()

if args.verbose:
    print("ASM INSRUCTIONS".center(N, "="))
    print(compiled_code)
    print()

output_file_path = "a.out"
if args.output is not None:
    output_file_path = args.output

asm_path = output_file_path + ".asm"
obj_path = output_file_path + ".o"

with open(asm_path, "w") as out_f:
    out_f.write(compiled_code)

if args.no_nasm:
    print(f"created: {asm_path}")
    exit(0)

result = subprocess.run(["nasm", "-f", "elf64", asm_path, "-o", obj_path])
if result.returncode != 0:
    print("nasm failed")
    exit(1)

if args.no_linker:
    os.remove(asm_path)
    print(f"created: {obj_path}")
    exit(0)

result = subprocess.run(["gcc", obj_path, "-o", output_file_path, "-no-pie"])
if result.returncode != 0:
    print("linker failed")
    exit(1)

os.remove(asm_path)
os.remove(obj_path)
print(f"created: {output_file_path}")
