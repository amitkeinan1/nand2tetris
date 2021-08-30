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


if __name__ == '__main__':
    test_subroutine()
