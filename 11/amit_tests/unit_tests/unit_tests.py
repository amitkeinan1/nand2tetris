from lxml.etree import Element, ElementTree

from CodeWriter import CodeWriter
from ExtendedXmlCompiler import ExtendedXmlCompiler

if __name__ == '__main__':
    file_name = "simple_expression"
    compiler = ExtendedXmlCompiler(file_name + ".jack", file_name + ".xml")
    expression = compiler.xml_compiler.compile_expression()[0]
    tree = ElementTree(expression)
    tree.write(file_name + ".xml", pretty_print=True)
    code_writer = CodeWriter(file_name + ".xml", file_name + ".vm")
    code_writer.write_expression_code(expression)
