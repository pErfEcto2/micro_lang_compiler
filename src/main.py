import argparse
import os
from compiler.compiler import Compiler
from tokenizer.tokenizer import Tokenizer
from parser.parser import Parser


parser = argparse.ArgumentParser()

parser.add_argument("-o", "--output", help="specify path to the output file", type=str)
parser.add_argument("-l", "--no-linker", help="dont use a linker, stop after nasm", action="store_true")
parser.add_argument("-n", "--no-nasm", help="dont use nasm, stop after compiling", action="store_true")
parser.add_argument("src", help="path to the file with a source code")

args = parser.parse_args()

if not os.path.exists(args.src):
    print(f"no such file or directory: {args.src}")
    exit(1)

with open(args.src, "r") as src_f:
    src_code = src_f.read()

tokenizer = Tokenizer(src_code)
tokens = tokenizer.tokenize()

print(tokens)

exit(0)

ast_parser = Parser(tokens)
ast_tree = ast_parser.parse()

# if ast_tree is None:
#     print("something went wrong, AST tree is empty")
#     exit(1)

compiler = Compiler(ast_tree)
compiled_code = compiler.compile()

# if compiled_code is None:
#     print("something went wrong, compiled code is empty")
#     exit(1)

output_file_path = "a.out"
if args.output is not None:
    output_file_path = args.output

with open(output_file_path, "w") as out_f:
    out_f.write(src_code)
    print(f"created: {output_file_path}")

if args.no_nasm:
    print("no nasm")
    exit(0)

# use nasm

if args.no_linker:
    print("no linker")
    exit(0)

# use ld
