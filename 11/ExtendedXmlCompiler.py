from typing import Optional

from SymbolTable import SymbolTable
from XmlCompiler import XmlCompiler
from lxml import etree
from lxml.etree import Element, ElementTree

from config import *


class ExtendedXmlCompiler:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_path: str, output_path: Optional[str]) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_path:
        :param output_path:
        """
        self.xml_compiler = XmlCompiler(input_path, None)
        self.symbol_table = SymbolTable()
        self.output_path = output_path

    @staticmethod
    def _get_type(element):
        return element.tag

    @staticmethod
    def _get_name(element):
        return element.text.strip()

    @staticmethod
    def _generate_tag(category, index, status):
        return f"identifier-{category}-{index}-{status}"


    def compile(self, write_to_file: bool = True) -> Optional[ElementTree]:
        xml_tree = self.xml_compiler.compile(write_to_file=False)

        for element in xml_tree.iter():
            element_type = self._get_type(element)
            if element_type == SUBROUTINE_DEC_TAG:
                self.symbol_table.start_subroutine()
            elif element_type == "identifier":
                element.tag = self._get_extended_type(element)

        if write_to_file:
            xml_tree.write(self.output_path, pretty_print=True)
        else:
            return xml_tree

    # TODO: how can we distinguish between className and varName in subroutine call
    # TODO: add running indexes
    def _get_extended_type(self, element):
        parent = element.getparent()
        parent_type = self._get_type(parent)
        if parent_type == CLASS_TAG:
            return self._generate_tag("class", 0, DEFINITION)
        elif parent_type == CLASS_VAR_DEC_TAG:
            var_name = self._get_name(element)
            var_kind = VAR_KINDS[self._get_name(parent[0])]
            self.symbol_table.define(var_name, self._get_name(parent[1]), var_kind)
            return self._generate_tag(var_kind, self.symbol_table.index_of(var_name), DEFINITION)
        else:
            return "identifier"


if __name__ == '__main__':
    compiler = ExtendedXmlCompiler("amit_tests/SquareMainJack.jack", "amit_tests/SquareMainExtended.xml")
    compiler.compile()
