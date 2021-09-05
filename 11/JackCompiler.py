"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys

from lxml import etree

from CodeWriter import CodeWriter
from ExtendedXmlCompiler import ExtendedXmlCompiler


# TODO: pass ConvertToBin

def compile_file(input_path: str, output_path: str) -> None:
    """Compiles a single file.

    Args:
        input_path (str): the path to the file to compile.
        output_path (str): writes all output to the file in this path.
    """
    compiler = ExtendedXmlCompiler(input_path)
    tree = compiler.compile(write_to_file=False)
    writer = CodeWriter(tree, output_path)
    writer.write_code()


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: JackCompiler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".jack":
            continue
        output_path = filename + ".vm"
        compile_file(input_path, output_path)
