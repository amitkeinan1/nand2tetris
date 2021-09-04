"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from typing import List, Union

from lxml import etree
from lxml.etree import Element

from SymbolTable import SymbolTable
from VMWriter import VMWriter
from config import *

regexpNS = "http://exslt.org/regular-expressions"  # TODO: put somewhere nicer


class CodeWriter:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, syntax_tree: etree, output_path: str) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param output_path:
        """
        self.parsed_code = syntax_tree
        self.output_path = output_path
        self.symbol_table = SymbolTable()
        self.vm_writer = VMWriter(open(output_path, 'w'))
        self.labels_count = 0

    def write_code(self) -> None:
        """ the main compile class. uses compile_class for the logic and write the contents to a file."""
        self.write_class_code(self.parsed_code.getroot())
        self.vm_writer.close_output_stream()

    def write_class_code(self, class_xml: Element) -> None:
        """Compiles a complete class."""
        # 'class' className '{' classVarDec* subroutineDec* '}'
        for class_var in class_xml.findall(f"./{CLASS_VAR_DEC_TAG}"):
            self.write_class_var_dec_code(class_var)
        for subroutine_dec in class_xml.findall(f"./{SUBROUTINE_DEC_TAG}"):
            self.write_subroutine_dec_code(subroutine_dec)

    def write_class_var_dec_code(self, var_dec: Element) -> None:
        """Compiles a static declaration or a field declaration."""
        # ('static' | 'field') type varName (',' varName)* ';'
        for element in var_dec:
            element_type = self._get_type(element)
            element_name = self._get_name(element)
            if element_type.startswith("identifier"):
                category, index, status, var_type = self._get_identifier_details(element_type)
                if status == DEFINITION:
                    self.symbol_table.define(element_name, var_type, category)

    def write_subroutine_dec_code(self, subroutine_dec: Element) -> None:
        """Compiles a complete method, function, or constructor."""
        # ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        subroutine_name = self._get_name(subroutine_dec[2])
        args_num = len(subroutine_dec.find(PARAMETER_LIST_TAG))
        self.vm_writer.write_function(subroutine_name, args_num)
        for var_dec in subroutine_dec.findall(VAR_DEC_TAG):
            self.write_var_dec_code(var_dec)
            subroutine_dec.find("subroutineBody").find("statements")
        self.write_statements_code(subroutine_dec.find("subroutineBody").find(STATEMENTS_TAG))

    def write_parameter_list_code(self) -> Union[List[Element], None]:  # TODO: is there anything to do here?
        # ((type varName) (',' type varName)*)?
        pass

    def write_var_dec_code(self, var_dec: Element) -> None:  # TODO: is there anything to do here?
        """Compiles a var declaration."""
        # 'var' type varName (',' varName)* ';'
        pass

    def write_statements_code(self, statements: Element) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        for statement in statements:
            if statement.tag == LET_TAG:
                self.write_let_code(statement)
            elif statement.tag == IF_TAG:
                self.write_if_code(statement)
            elif statement.tag == WHILE_TAG:
                self.write_while_code(statement)
            elif statement.tag == DO_TAG:
                self.write_do_code(statement)
            elif statement.tag == RETURN_TAG:
                self.write_return_code(statement)

    def write_do_code(self, do_statement: Element) -> None:
        """Compiles a do statement."""
        self.write_expression_list_code(do_statement.find(EXPRESSION_LIST_TAG))
        method_name = do_statement.find("//*[re:test(., 'identifier-subroutine-^[0-9]+$-usage', 'i')]",
                                              namespaces={'re': regexpNS}).text
        args_num = len(do_statement.findall(f"./{EXPRESSION_LIST_TAG}/{EXPRESSION_TAG}"))
        self.vm_writer.write_call(method_name, args_num)

    def write_let_code(self, let_statement: Element) -> None:  # TODO
        """Compiles a let statement."""
        pass

    def write_while_code(self, while_statement: Element) -> None:
        """Compiles a while statement."""
        start_label = self._generate_label("while-L1")
        out_label = self._generate_label("while-L2")

        self.vm_writer.write_label(start_label)  # label L1
        # !(cond):
        condition = while_statement.find(EXPRESSION_TAG)
        self._negate_and_push_condition(condition)

        self.vm_writer.write_if(out_label)  # if-goto L2
        self.write_statements_code(while_statement.find(STATEMENTS_TAG))  # execute s
        self.vm_writer.write_goto(start_label)  # goto L1
        self.vm_writer.write_label(out_label)  # label L2

    def write_return_code(self, return_statement: Element) -> None:
        """Compiles a return statement."""
        # push result and return
        return_expression = return_statement.find(EXPRESSION_TAG)
        if return_expression is not None:
            self.write_expression_code(return_expression)
        self.vm_writer.write_return()

    def write_if_code(self, if_statement: Element) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        false_label = self._generate_label("if-L1")  # TODO: what if there's no else statement
        true_label = self._generate_label("if-L2")
        statements = if_statement.findall(STATEMENTS_TAG)

        # !(cond):
        condition = if_statement.find(EXPRESSION_TAG)
        self._negate_and_push_condition(condition)

        self.vm_writer.write_if(false_label)  # if-goto L1
        self.write_statements_code(statements[0])  # execute s1
        self.vm_writer.write_goto(true_label)  # goto-L2
        self.vm_writer.write_label(false_label)  # label L1
        self.write_statements_code(statements[1])  # execute s2 TODO: should it be optional?
        self.vm_writer.write_label(true_label)  # label L2

    def write_expression_code(self, expression: Element) -> None:  # TODO
        """Compiles an expression."""
        pass

    def write_term_code(self) -> Union[List[Element], None]:  # TODO
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # integerConstant | stringConstant | keywordConstant | varName | varName '['expression']' | subroutineCall |
        # '(' expression ')' | unaryOp term
        pass

    def write_expression_list_code(self, expression_list: Element) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # (expression (',' expression)* )?
        for expression in expression_list.findall(EXPRESSION_TAG):
            self.write_expression_code(expression)

    def write_subroutine_body_code(self, subroutine: Element) -> None:
        for var_dec in subroutine.findall(VAR_DEC_TAG):
            self.write_var_dec_code(var_dec)
        self.write_statements_code(subroutine.find(STATEMENTS_TAG))

    # helper methods
    def _generate_label(self, name: str) -> str:
        label = f"{name} - {self.labels_count}"
        self.labels_count += 1
        return label

    def _negate_and_push_condition(self, condition_expression):
        self.write_expression_code(condition_expression)
        self.vm_writer.write_arithmetic("NOT")

    @staticmethod
    def _get_identifier_details(element_type):
        details = element_type.split("-")
        assert len(details) == 5
        return details[1:]

    # TODO: code dup
    @staticmethod
    def _get_type(element):
        return element.tag

    # TODO: code dup
    @staticmethod
    def _get_name(element):
        return element.text.strip()


if __name__ == '__main__':
    file_name = "SquareMain"
    syntax_tree = etree.parse(f"amit_tests/{file_name}Extended.xml")
    code_writer = CodeWriter(syntax_tree, f"amit_tests/{file_name}VM.vm")
    code_writer.write_code()
