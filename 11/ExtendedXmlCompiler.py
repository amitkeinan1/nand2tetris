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
            if len(element) != 0:  # if this is not a leaf
                for index, child_element in enumerate(element):
                    element_type = self._get_type(child_element)
                    if element_type == SUBROUTINE_DEC_TAG:
                        self.symbol_table.start_subroutine()
                    elif element_type == "identifier":
                        child_element.tag = self._get_extended_type(child_element, index)

        if write_to_file:
            xml_tree.write(self.output_path, pretty_print=True)
        else:
            return xml_tree

    def _handle_var_name_defined(self, element, parent):
        var_name = self._get_name(element)
        var_kind = VAR_KINDS[self._get_name(parent[0])]
        self.symbol_table.define(var_name, self._get_name(parent[1]), var_kind)
        return self._generate_tag(var_kind, self.symbol_table.index_of(var_name), DEFINITION)

    # TODO: how can we distinguish between className and varName in subroutine call
    # TODO: add running indexes
    def _get_extended_type(self, element: Element, index: int):
        parent = element.getparent()
        parent_type = self._get_type(parent)

        if parent_type == CLASS_TAG:
            return self._generate_tag("class", 0, DEFINITION)

        elif parent_type == CLASS_VAR_DEC_TAG:
            return self._handle_var_name_defined(element, parent)

        elif parent_type == SUBROUTINE_DEC_TAG:
            if index == 1:
                return self._generate_tag("class", 0, DEFINITION)
            else:
                self.symbol_table.start_subroutine()
                return self._generate_tag("subroutine", 0, DEFINITION)

        elif parent_type == VAR_DEC_TAG:
            if index == 1:
                return self._generate_tag("class", 0, USAGE)
            else:
                return self._handle_var_name_defined(element, parent)

        else:
            return "identifier"


if __name__ == '__main__':
    compiler = ExtendedXmlCompiler("amit_tests/SquareMainJack.jack", "amit_tests/SquareMainExtended.xml")
    compiler.compile()
