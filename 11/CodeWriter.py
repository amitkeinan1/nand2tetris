"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from typing import List, Union

from lxml import etree
from lxml.etree import Element, ElementTree
from xml.dom import minidom

from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter
from config import *
from jack_syntax import OPERATORS, UNARY_OPERATORS, KEYWORD_CONSTANTS
from xml_utils import xml_write_patch


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

    def _write_xml(self, xml_root):
        """ takes an xml root and write its tree to xml file in the required format. """
        tree: etree.ElementTree = etree.ElementTree(xml_root)
        tree_string = etree.tostring(tree, method="c14n", xml_declaration=False).decode()
        minidom_tree = minidom.parseString(tree_string)
        minidom_tree.firstChild.__class__.writexml = xml_write_patch(minidom_tree.firstChild.__class__.writexml)

        lines = minidom_tree.toprettyxml().split("\n")[
                1:-1]  # remove first and last line to be exactly consistent with the given tests format
        with open(self.output_path, 'w') as f:
            f.writelines([line.replace("\t", "  ") + '\n' for line in lines])  # replace tabs with double spaces to
            # be exactly consistent with the given tests format

    def write_code(self) -> None:
        """ the main compile class. uses compile_class for the logic and write the contents to a file."""
        self.write_class_code(self.parsed_code.find(CLASS_TAG))

    def write_class_code(self, class_xml: Element) -> None:
        """Compiles a complete class."""
        # 'class' className '{' classVarDec* subroutineDec* '}'
        self.symbol_table = SymbolTable()
        for class_var in class_xml.find(f"./{CLASS_VAR_DEC_TAG}"):
            self.write_class_var_dec_code(class_var)
        for subroutine_dec in class_xml.find(f"./{SUBROUTINE_DEC_TAG}"):
            self.write_subroutine_dec_code(subroutine_dec)

    def write_class_var_dec_code(self, var_dec: Element) -> None:  # TODO
        """Compiles a static declaration or a field declaration."""
        # ('static' | 'field') type varName (',' varName)* ';'
        var_dec_root = Element("classVarDec")

        elements = self._sequence_compiling_with_kwargs([
            (self.get_curr_token_if_one_of_conditions, {"expected_tokens": ["static", "field"]}),
            (self.compile_type, {}),
            (self._get_curr_token_if_condition, {"expected_type": TokenTypes.IDENTIFIER}),
            (self._asterisk_compiling, {"compile_method": self._compile_comma_and_var_name}),
            (self._get_curr_token_if_condition, {"expected_token": ";"})
        ])
        return self._add_elements(var_dec_root, elements)

    def write_subroutine_dec_code(self, subroutine_dec: Element) -> None:  # TODO
        """Compiles a complete method, function, or constructor."""
        self.symbol_table.start_subroutine()
        subroutine_root = Element("subroutineDec")

        elements = self._sequence_compiling_with_kwargs([
            (self.get_curr_token_if_one_of_conditions, {"expected_tokens": ["constructor", "function", "method"]}),
            (self._get_curr_token_if_condition_or_compile_method,
             {"expected_type": None, "expected_token": "void", "compile_method":
                 self.compile_type}),
            (self._get_curr_token_if_condition, {"expected_type": TokenTypes.IDENTIFIER}),
            (self._get_curr_token_if_condition, {"expected_token": "("}),
            (self.write_parameter_list_code, {}),
            (self._get_curr_token_if_condition, {"expected_token": ")"}),
            (self.write_subroutine_body_code, {})
        ])
        return self._add_elements(subroutine_root, elements)

    def _inner_compile_parameter_list(self) -> Union[List[Element], None]:  # TODO
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        # (type varName) (',' type varName)*
        return self._sequence_compiling_with_kwargs([
            (self.compile_type, {}),
            (self._get_curr_token_if_condition, {'expected_type': TokenTypes.IDENTIFIER}),
            (self._asterisk_compiling, {'compile_method': self._compile_comma_and_type_and_var_name})
        ])

    def write_parameter_list_code(self) -> Union[List[Element], None]:  # TODO
        # ((type varName) (',' type varName)*)?
        parameter_list_root = Element("parameterList")
        elements = self._question_mark_compiling(self._inner_compile_parameter_list)
        return self._add_elements(parameter_list_root, elements)

    def write_var_dec_code(self, var_dec: Element) -> None:  # TODO
        """Compiles a var declaration."""
        # 'var' type varName (',' varName)* ';'
        var_dec_root = Element("varDec")
        elements = self._sequence_compiling_with_kwargs([
            (self._get_curr_token_if_condition, {"expected_token": "var"}),
            (self.compile_type, {}),
            (self._get_curr_token_if_condition, {"expected_type": TokenTypes.IDENTIFIER}),
            (self._asterisk_compiling_with_args, {"compile_method": self._sequence_compiling_with_kwargs,
                                                  "compile_methods_and_kwargs":
                                                      [(self._get_curr_token_if_condition,
                                                        {'expected_token': ','}),
                                                       (self._get_curr_token_if_condition, {
                                                           'expected_type':
                                                               TokenTypes.IDENTIFIER})]}),
            (self._get_curr_token_if_condition, {"expected_token": ";"})
        ])

        return self._add_elements(var_dec_root, elements)

    def write_statements_code(self, statements: Element) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        for statement in statements.findall():
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
        method_name = ""  # TODO: extract method name
        args_num = len(do_statement.findall(f"./{EXPRESSION_LIST_TAG}/{EXPRESSION_TAG}"))
        self.vm_writer.write_call(method_name, args_num)

    def _compile_normal_subroutine_call(self) -> Union[List[Element], None]:

        # subroutineName '(' expressionList ')'
        return self._sequence_compiling_with_kwargs([
            (self._get_curr_token_if_condition, {"expected_type": TokenTypes.IDENTIFIER}),
            (self._get_curr_token_if_condition, {"expected_token": '('}),
            (self.write_expression_list_code, {}),
            (self._get_curr_token_if_condition, {"expected_token": ')'})]
        )

    def _compile_class_subroutine_call(self) -> Union[List[Element], None]:
        # (className | varName) '.' subroutineName '(' expressionList ')'
        return self._sequence_compiling_with_kwargs([
            (self._get_curr_token_if_condition, {'expected_type': TokenTypes.IDENTIFIER}),
            (self._get_curr_token_if_condition, {'expected_token': '.'}),
            (self._get_curr_token_if_condition, {'expected_type': TokenTypes.IDENTIFIER}),
            (self._get_curr_token_if_condition, {'expected_token': '('}),
            (self.write_expression_list_code, {}),
            (self._get_curr_token_if_condition, {'expected_token': ')'})

        ])

    def _compile_subroutine_call(self) -> Union[List[Element], None]:
        # normalSubroutineCall | classSubroutineCall
        return self._or_compiling([self._compile_normal_subroutine_call, self._compile_class_subroutine_call])

    def _compile_array_accessor(self) -> Union[List[Element], None]:
        return self._sequence_compiling_with_kwargs([
            (self._get_curr_token_if_condition, {"expected_token": "["}),
            (self.write_expression_code, {}),
            (self._get_curr_token_if_condition, {"expected_token": "]"})
        ])

    def write_let_code(self, let_statement: Element) -> None:  # TODO
        """Compiles a let statement."""
        # 'let' varName ('[' expression ']')? '=' expression ';'
        let_root = Element("letStatement")
        elements = self._sequence_compiling_with_kwargs([
            (self._get_curr_token_if_condition, {"expected_token": "let"}),
            (self._get_curr_token_if_condition, {"expected_type": TokenTypes.IDENTIFIER}),
            (self._question_mark_compiling, {"compile_method": self._compile_array_accessor}),
            (self._get_curr_token_if_condition, {"expected_token": "="}),
            (self.write_expression_code, {}),
            (self._get_curr_token_if_condition, {"expected_token": ";"})
        ])
        return self._add_elements(let_root, elements)

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
        false_label = self._generate_label("if-L1") # TODO: what if there's no else statement
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

    def _compile_op(self) -> Union[List[Element], None]:
        return self.get_curr_token_if_one_of_conditions(expected_tokens=OPERATORS)

    def _compile_unary_op(self) -> Union[List[Element], None]:
        return self.get_curr_token_if_one_of_conditions(expected_tokens=UNARY_OPERATORS)

    def _compile_keyword_constant(self) -> Union[List[Element], None]:
        return self.get_curr_token_if_one_of_conditions(expected_tokens=KEYWORD_CONSTANTS)

    def _compile_op_term(self) -> Union[List[Element], None]:
        # op term
        return self._sequence_compiling([self._compile_op, self.write_term_code])

    def write_expression_code(self, expression: Element) -> None:  # TODO
        """Compiles an expression."""
        expression_root = Element("expression")
        elements = self._sequence_compiling_with_kwargs([
            (self.write_term_code, {}),
            (self._asterisk_compiling, {'compile_method': self._compile_op_term})
        ])
        return self._add_elements(expression_root, elements)

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
        term_root = Element("term")
        next_token = self.tokenizer.next_token()
        if self.tokenizer.token_type() == TokenTypes.IDENTIFIER and next_token:
            if next_token == "[":
                elements = self._sequence_compiling_with_kwargs([
                    (self._get_curr_token_if_condition, {"expected_type": TokenTypes.IDENTIFIER}),
                    (self._get_curr_token_if_condition, {"expected_token": '['}),
                    (self.write_expression_code, {}),
                    (self._get_curr_token_if_condition, {"expected_token": ']'})
                ])
            elif next_token == "." or next_token == "(":
                elements = self._compile_subroutine_call()
            else:
                elements = self._get_curr_token_if_condition(expected_type=TokenTypes.IDENTIFIER)
        else:
            elements = self._or_compiling([
                self._compile_callable_wrapper(self._get_curr_token_if_condition, expected_type=TokenTypes.INT_CONST),
                self._compile_callable_wrapper(self._get_curr_token_if_condition,
                                               expected_type=TokenTypes.STRING_CONST),
                self._compile_keyword_constant,
                self._compile_callable_wrapper(self._sequence_compiling_with_kwargs, [
                    (self._get_curr_token_if_condition, {"expected_token": '('}),
                    (self.write_expression_code, {}),
                    (self._get_curr_token_if_condition, {"expected_token": ')'})
                ]),
                self._compile_callable_wrapper(self._sequence_compiling, [self._compile_unary_op, self.write_term_code])
            ])
        return self._add_elements(term_root, elements)

    def write_expression_list_code(self, expression_list: Element) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # (expression (',' expression)* )?
        for expression in expression_list.findall(EXPRESSION_TAG):
            self.write_expression_code(expression)

    def write_subroutine_body_code(self, subroutine: Element) -> None:
        for var_dec in subroutine.findall(VAR_DEC_TAG):
            self.write_var_dec_code(var_dec)
        self.write_statements_code(subroutine.find(STATEMENTS_TAG))

    def _compile_comma_and_var_name(self) -> Union[List[Element], None]:
        return self._sequence_compiling_with_kwargs([
            (self._get_curr_token_if_condition, {"expected_token": ","}),
            (self._get_curr_token_if_condition, {"expected_type": TokenTypes.IDENTIFIER})
        ])

    def _compile_comma_and_type_and_var_name(self) -> Union[List[Element], None]:
        return self._sequence_compiling_with_kwargs([
            (self._get_curr_token_if_condition, {"expected_token": ","}),
            (self.compile_type, {}),
            (self._get_curr_token_if_condition, {"expected_type": TokenTypes.IDENTIFIER})
        ])

    # helper methods
    def _generate_label(self, name: str) -> str:
        label = f"{name} - {self.labels_count}"
        self.labels_count += 1
        return label

    def _negate_and_push_condition(self, condition_expression):
        self.write_expression_code(condition_expression)
        self.vm_writer.write_arithmetic("NOT")
