from lxml import etree
from lxml.etree import Element

from CompilationEngine import CompilationEngine


def test_subroutines():
    root = Element("root")
    c = CompilationEngine("subroutines.jack", "Main.xml")
    c._add_elements(root, c._asterisk_compiling(c.compile_subroutine))
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)


def test_subroutine():
    root = Element("root")
    c = CompilationEngine("subroutine.jack", "Main.xml")
    c._add_elements(root, c.compile_subroutine())
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)


def test_subroutine_body():
    root = Element("root")
    c = CompilationEngine("subroutine_body.jack", "Main.xml")
    c._add_elements(root, c.compile_subroutine_body())
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)


def test_statements():
    root = Element("root")
    c = CompilationEngine("statements.jack", "Main.xml")
    c._add_elements(root, c.compile_statements())
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)


def test_statement():
    root = Element("root")
    c = CompilationEngine("statement.jack", "Main.xml")
    c._add_elements(root, c.compile_statement())
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)


def test_let():
    root = Element("root")
    c = CompilationEngine("let.jack", "Main.xml")
    c._add_elements(root, c.compile_let())
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)


def test_expression():
    root = Element("root")
    c = CompilationEngine("expression.jack", "Main.xml")
    c._add_elements(root, c.compile_expression())
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)


def test_term():
    root = Element("root")
    c = CompilationEngine("term.jack", "Main.xml")
    c._add_elements(root, c.compile_term())
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)


def test_subroutine_call():
    root = Element("root")
    c = CompilationEngine("subroutine_call.jack", "Main.xml")
    c._add_elements(root, c._compile_subroutine_call())
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)


def test_class_subroutine_call():
    root = Element("root")
    c = CompilationEngine("class_subroutine_call.jack", "Main.xml")
    c._add_elements(root, c._compile_class_subroutine_call())
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)


def test_expression_list():
    root = Element("root")
    c = CompilationEngine("expression_list.jack", "Main.xml")
    c._add_elements(root, c.compile_expression_list())
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)


def test_nums():
    root = Element("root")
    c = CompilationEngine("nums.jack", "Main.xml")
    c._add_elements(root, c._sequence_compiling([c._compile_op, c._compile_op]))
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)


if __name__ == '__main__':
    # test_nums()
    test_expression_list()
    # test_class_subroutine_call()
    # test_subroutine_call()
    # test_term()
    # test_expression()
    # test_let()
    # test_statements()
    # test_subroutine_body()
    # test_subroutine()
    # test_subroutines()
