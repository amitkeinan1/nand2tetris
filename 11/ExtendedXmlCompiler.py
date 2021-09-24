from typing import Optional

from lxml.etree import Element, ElementTree

from SymbolTable import SymbolTable
from XmlCompiler import XmlCompiler
from config import *

from xml_utils import get_text, get_type


class ExtendedXmlCompiler:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_path: str, output_path: Optional[str] = None) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_path:
        :param output_path:
        """
        self.xml_compiler = XmlCompiler(input_path, None)
        self.symbol_table = SymbolTable()
        self.output_path = output_path
        self.class_name = None

    @staticmethod
    def _get_type(element):
        return element.tag

    @staticmethod
    def _get_name(element):
        return element.text.strip()

    @staticmethod
    def _generate_tag(category, index, status, var_type="UNK"):
        return f"identifier-{category}-{index}-{status}-{var_type}"

    def _extend_tree(self, xml_tree, write_to_file):
        for element in xml_tree.iter():
            if len(element) != 0:  # if this is not a leaf
                for index, child_element in enumerate(element):
                    element_type = get_type(child_element)
                    if element_type == SUBROUTINE_DEC_TAG:
                        self.symbol_table.start_subroutine()
                    elif element_type == "identifier":
                        child_element.tag = self._get_extended_type(child_element, index)
        return xml_tree

    def compile(self, write_to_file: bool = True) -> Optional[ElementTree]:
        xml_tree = self.xml_compiler.compile(write_to_file=False)
        self.class_name = get_text(xml_tree.getroot()[1])
        self._add_subroutine_symbols(xml_tree)

        xml_tree = self._extend_tree(xml_tree, write_to_file)

        if write_to_file:
            xml_tree.write(self.output_path, pretty_print=True)
        else:
            return xml_tree

    def _add_subroutine_symbols(self, xml_tree):
        for subroutine_dec in xml_tree.findall(f"./{SUBROUTINE_DEC_TAG}"):
            for index, element in enumerate(subroutine_dec):
                element_type = get_type(element)
                if element_type == "identifier":
                    subroutine_name = get_text(element)
                    self.symbol_table.define(subroutine_name, "subroutine", get_text(subroutine_dec[0]))
                    break

    def _handle_var_defined_params_list(self, element, parent, index):
        var_kind = VAR_KINDS["argument"]
        var_name = get_text(element)
        var_type = get_text(parent[index - 1])
        self.symbol_table.define(var_name, var_type, var_kind)
        return self._generate_tag(var_kind, self.symbol_table.index_of(var_name), DEFINITION, var_type)

    def _handle_var_defined(self, element, parent):
        var_name = get_text(element)
        var_kind = VAR_KINDS[get_text(parent[0])]
        var_type = get_text(parent[1])
        self.symbol_table.define(var_name, var_type, var_kind)
        return self._generate_tag(var_kind, self.symbol_table.index_of(var_name), DEFINITION, var_type)

    def _handle_subroutine_call(self, element, index, parent, index_of_call):
        index_in_call = index - index_of_call
        is_normal_call = get_text(parent[index_of_call + 1]) != '.'
        if is_normal_call:
            assert index_in_call == 0
            return self._generate_tag("subroutine", 0, USAGE,
                                      self.symbol_table.kind_of(get_text(parent[index_of_call])))
        else:
            if index_in_call == 0:
                if self.symbol_table.kind_of(get_text(element)) is None:
                    return self._generate_tag("class", 0, USAGE)
                else:
                    return self._handle_var_used(element)
            if index_in_call == 2:
                return self._generate_tag("subroutine", 0, USAGE,
                                          self.symbol_table.kind_of(get_text(parent[index_of_call + 2])))

    def _handle_var_used(self, element):
        var_name = get_text(element)
        var_kind = self.symbol_table.kind_of(var_name)
        var_index = self.symbol_table.index_of(var_name)
        var_type = self.symbol_table.type_of(var_name)
        return self._generate_tag(var_kind, var_index, USAGE, var_type)

    def _get_extended_type(self, element: Element, index: int):
        parent = element.getparent()
        parent_type = get_type(parent)

        if parent_type == CLASS_TAG:
            return self._generate_tag("class", 0, DEFINITION)
        elif parent_type == CLASS_VAR_DEC_TAG:
            if index == 1:
                return self._generate_tag("class", 0, USAGE)
            else:
                return self._handle_var_defined(element, parent)

        elif parent_type == SUBROUTINE_DEC_TAG:
            if index == 1:
                return self._generate_tag("class", 0, USAGE)
            else:
                self.symbol_table.start_subroutine()
                subroutine_name = get_text(element)
                # self.symbol_table.define(subroutine_name, "subroutine", get_text(parent[0]))
                if self.symbol_table.kind_of(subroutine_name) == "method":
                    self.symbol_table.define("this", None, "ARG")
                return self._generate_tag("subroutine", 0, DEFINITION, self.symbol_table.kind_of(subroutine_name))

        elif parent_type == PARAMETER_LIST_TAG:
            if index % 3 == 0:
                return self._generate_tag("class", 0, USAGE)
            elif index % 3 == 1:
                return self._handle_var_defined_params_list(element, parent, index)
            else:
                raise Exception()

        elif parent_type == VAR_DEC_TAG:
            if index == 1:
                return self._generate_tag("class", 0, USAGE)
            else:
                return self._handle_var_defined(element, parent)

        elif parent_type == LET_TAG:
            assert index == 1
            return self._handle_var_used(element)

        elif parent_type == DO_TAG:
            return self._handle_subroutine_call(element, index, parent, 1)

        elif parent_type == TERM_TAG:
            if len(parent) == 1:
                return self._handle_var_used(element)
            elif get_text(parent[1]) in ["(", "."]:
                return self._handle_subroutine_call(element, index, parent, 0)
            elif get_text(parent[1]) == "[":
                assert index == 0
                return self._handle_var_used(element)
            else:
                raise Exception()

        else:
            return "identifier"


if __name__ == '__main__':
    file_name = "SquareMain"
    compiler = ExtendedXmlCompiler(f"amit_tests/{file_name}Jack.jack", f"amit_tests/{file_name}Extended.xml")
    compiler.compile()
