from lxml import etree
from lxml.etree import Element

from CompilationEngine import CompilationEngine


def test_subroutines():
    root = Element("root")
    c = CompilationEngine("subroutines.jack", "Amit/Main.xml")
    c._add_elements(root, c._asterisk_compiling(c.compile_subroutine))
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)


def test_subroutine():
    root = Element("root")
    c = CompilationEngine("subroutine.jack", "Amit/Main.xml")
    c._add_elements(root, c.compile_subroutine())
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)


def test_subroutine_body():
    root = Element("root")
    c = CompilationEngine("subroutine_body.jack", "Amit/Main.xml")
    c._add_elements(root, c.compile_subroutine_body())
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)


def test_statements():
    root = Element("root")
    c = CompilationEngine("statements.jack", "Amit/Main.xml")
    c._add_elements(root, c.compile_statements())
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)


def test_statement():
    root = Element("root")
    c = CompilationEngine("statement.jack", "Amit/Main.xml")
    c._add_elements(root, c.compile_statement())
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)

def test_let():
    root = Element("root")
    c = CompilationEngine("let.jack", "Amit/Main.xml")
    c._add_elements(root, c.compile_let())
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)


if __name__ == '__main__':
    test_let()
    # test_statements()
    # test_subroutine_body()
    # test_subroutine()
    # test_subroutines()
