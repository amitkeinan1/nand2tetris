"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from typing import List, Callable, Tuple, Union, Optional

from lxml import etree
from lxml.etree import Element, ElementTree
from xml.dom import minidom

from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter
from config import *
from jack_syntax import OPERATORS, UNARY_OPERATORS, KEYWORD_CONSTANTS
from xml_utils import xml_write_patch


class XmlCompiler:
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
        self.tokenizer = JackTokenizer(input_path)
        self.output_path = output_path
        self.symbol_table = SymbolTable()
        self.vm_writer = VMWriter(output_path)

    def _write_xml(self, xml_root):
        """ takes an xml root and write its tree to xml file in the required format. """
        tree: ElementTree = ElementTree(xml_root)
        tree_string = etree.tostring(tree, method="c14n", xml_declaration=False).decode()
        minidom_tree = minidom.parseString(tree_string)
        minidom_tree.firstChild.__class__.writexml = xml_write_patch(minidom_tree.firstChild.__class__.writexml)

        lines = minidom_tree.toprettyxml().split("\n")[
                1:-1]  # remove first and last line to be exactly consistent with the given tests format
        with open(self.output_path, 'w') as f:
            f.writelines([line.replace("\t", "  ") + '\n' for line in lines])  # replace tabs with double spaces to
            # be exactly consistent with the given tests format

    def compile(self, write_to_file: bool = True) -> Optional[ElementTree]:
        """ the main compile class. uses compile_class for the logic and write the contents to a file."""
        root = self.compile_class()
        if root is None:
            raise Exception("class could not be compiled.")
        if write_to_file:
            self._write_xml(root)
        else:
            return ElementTree(root)

    # helper methods
    @staticmethod
    def _compile_callable_wrapper(compile_method: Callable, *args, **kwargs) -> Callable:
        return lambda: compile_method(*args, **kwargs)

    def _get_curr_token(self) -> Union[List[Element], None]:
        """
        get the current tokenizer token as a single value list contains one xml element
        """
        if self.tokenizer.curr_index == len(self.tokenizer.tokens):
            return None
        token_element = Element(self.tokenizer.token_type_repr())
        token_element.text = f" {self.tokenizer.token_repr()} "
        self.tokenizer.advance()
        return [token_element]

    def _get_curr_token_if_condition(self, expected_type=None, expected_token=None) -> Union[List[Element], None]:

        if self.tokenizer.curr_index == len(self.tokenizer.tokens):
            return None
        if (expected_type is None or self.tokenizer.token_type() == expected_type) and (
                expected_token is None or self.tokenizer.curr_token() == expected_token):
            return self._get_curr_token()
        else:
            return None

    def _get_curr_token_if_condition_or_compile_method(self, expected_type, expected_token, compile_method) -> Union[
        List[Element], None]:
        elements_to_add = self._get_curr_token_if_condition(expected_type, expected_token)
        if not elements_to_add:
            elements_to_add = compile_method()
        return elements_to_add

    def get_curr_token_if_one_of_conditions(self, expected_types=None, expected_tokens=None) -> Union[
        List[Element], None]:
        if expected_types is None and expected_tokens is None:
            raise ValueError("At least one of the arguments: expected_types and expected_tokens should not be None")
        if expected_types is not None and expected_tokens is not None and (len(expected_types) != len(expected_tokens)):
            raise ValueError("When providing both expected_types and expected_tokens they must have the same length")
        if expected_types is None:
            expected_types = [None for _ in range(len(expected_tokens))]
        if expected_tokens is None:
            expected_tokens = [None for _ in range(len(expected_types))]

        for expected_type, expected_token in zip(expected_types, expected_tokens):
            elements_to_add = self._get_curr_token_if_condition(expected_type, expected_token)
            if elements_to_add:
                return elements_to_add
        return None

    def _compile_safely(self, compile_method: Callable) -> Union[List[Element], None]:
        """ wrapper method. takes a compile method and calls it safely, that is if it fails it takes the tokenizer
        back. """
        initial_token_index = self.tokenizer.curr_index
        res = compile_method()
        if res is None:
            self.tokenizer.curr_index = initial_token_index
        return res

    def _or_compiling(self, compile_methods: List[Callable]) -> Union[List[Element], None]:
        """ takes list of compile methods that match pattern_1, ..., pattern_n and matches pattern_1 | ... |
        pattern_n """

        for compile_method in compile_methods:
            curr_elements = self._compile_safely(compile_method)
            if curr_elements:
                return curr_elements
        return None

    def _asterisk_compiling(self, compile_method: Callable) -> List[Element]:
        """ takes compile method that matches pattern and matches (pattern)*"""
        elements = []
        curr_elements = self._compile_safely(compile_method)
        while curr_elements:
            elements += curr_elements
            curr_elements = self._compile_safely(compile_method)

        return elements

    def _asterisk_compiling_with_args(self, compile_method: Callable, *args, **kwargs) -> List[Element]:
        def injected_compile_method():
            return compile_method(*args, **kwargs)

        return self._asterisk_compiling(injected_compile_method)

    def _question_mark_compiling(self, compile_method: Callable) -> List[Element]:
        """ takes compile method that matches pattern and matches (pattern)?"""
        curr_elements = self._compile_safely(compile_method)
        if curr_elements:
            return curr_elements
        else:
            return []

    def _sequence_compiling(self, compile_methods: List[Callable]) -> Union[List[Element], None]:
        """ compiles a list of compile methods one after the other. """
        elements_lists = []
        for compile_method in compile_methods:
            elements = self._compile_safely(compile_method)
            if elements is not None:
                elements_lists.append(elements)
            else:
                return None
        return [elem for elements in elements_lists for elem in elements]

    def _sequence_compiling_with_kwargs(self, compile_methods_and_kwargs: List[Tuple[Callable, dict]]) -> List[Element]:
        """ wrapper for sequence compiling that enables sending arguments to the compile methods"""
        compile_methods = [lambda method_and_kwargs=method_and_kwargs: method_and_kwargs[0](**method_and_kwargs[1]) for
                           method_and_kwargs in compile_methods_and_kwargs]
        return self._sequence_compiling(compile_methods)

    def _add_elements(self, root: Element, elements: List[Element]) -> Union[List[Element], None]:
        """ adds a list of elements to tree root if the list is not None"""
        if elements is None:
            return None
        for element in elements:
            root.append(element)
        return [root]

    # compile methods
    def compile_class(self) -> Element:
        """Compiles a complete class."""
        # 'class' className '{' classVarDec* subroutineDec* '}'
        class_root = Element(CLASS_TAG)
        elements = self._sequence_compiling_with_kwargs(
            [
                (self._get_curr_token_if_condition, {"expected_type": TokenTypes.KEYWORD, "expected_token": "class"}),
                (self._get_curr_token_if_condition, {"expected_type": TokenTypes.IDENTIFIER}),
                (self._get_curr_token_if_condition, {"expected_type": TokenTypes.SYMBOL, "expected_token": "{"}),
                (self._asterisk_compiling, {"compile_method": self.compile_class_var_dec}),
                (self._asterisk_compiling, {"compile_method": self.compile_subroutine}),
                (self._get_curr_token_if_condition, {"expected_type": TokenTypes.SYMBOL, "expected_token": "}"})
            ]
        )

        res = self._add_elements(class_root, elements)
        if res is None:
            return None
        else:
            return res[0]

    def compile_class_var_dec(self) -> Union[List[Element], None]:
        """Compiles a static declaration or a field declaration."""
        # ('static' | 'field') type varName (',' varName)* ';'
        var_dec_root = Element(CLASS_VAR_DEC_TAG)

        elements = self._sequence_compiling_with_kwargs([
            (self.get_curr_token_if_one_of_conditions, {"expected_tokens": ["static", "field"]}),
            (self.compile_type, {}),
            (self._get_curr_token_if_condition, {"expected_type": TokenTypes.IDENTIFIER}),
            (self._asterisk_compiling, {"compile_method": self._compile_comma_and_var_name}),
            (self._get_curr_token_if_condition, {"expected_token": ";"})
        ])
        return self._add_elements(var_dec_root, elements)

    def compile_subroutine(self) -> Union[List[Element], None]:
        """Compiles a complete method, function, or constructor."""
        subroutine_root = Element(SUBROUTINE_DEC_TAG)

        elements = self._sequence_compiling_with_kwargs([
            (self.get_curr_token_if_one_of_conditions, {"expected_tokens": ["constructor", "function", "method"]}),
            (self._get_curr_token_if_condition_or_compile_method,
             {"expected_type": None, "expected_token": "void", "compile_method":
                 self.compile_type}),
            (self._get_curr_token_if_condition, {"expected_type": TokenTypes.IDENTIFIER}),
            (self._get_curr_token_if_condition, {"expected_token": "("}),
            (self.compile_parameter_list, {}),
            (self._get_curr_token_if_condition, {"expected_token": ")"}),
            (self.compile_subroutine_body, {})
        ])
        return self._add_elements(subroutine_root, elements)

    def _inner_compile_parameter_list(self) -> Union[List[Element], None]:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        # (type varName) (',' type varName)*
        return self._sequence_compiling_with_kwargs([
            (self.compile_type, {}),
            (self._get_curr_token_if_condition, {'expected_type': TokenTypes.IDENTIFIER}),
            (self._asterisk_compiling, {'compile_method': self._compile_comma_and_type_and_var_name})
        ])

    def compile_parameter_list(self) -> Union[List[Element], None]:
        # ((type varName) (',' type varName)*)?
        parameter_list_root = Element(PARAMETER_LIST_TAG)
        elements = self._question_mark_compiling(self._inner_compile_parameter_list)
        return self._add_elements(parameter_list_root, elements)

    def compile_var_dec(self) -> Union[List[Element], None]:
        """Compiles a var declaration."""
        # 'var' type varName (',' varName)* ';'
        var_dec_root = Element(VAR_DEC_TAG)
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

    def compile_statement(self):
        return self._or_compiling(
            [self.compile_let, self.compile_if, self.compile_while, self.compile_do, self.compile_return])

    def compile_statements(self) -> List[Element]:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        statements_root = Element(STATEMENTS_TAG)
        return self._add_elements(statements_root, self._asterisk_compiling(self.compile_statement))

    def compile_do(self) -> Union[List[Element], None]:
        """Compiles a do statement."""
        do_root = Element(DO_TAG)
        elements = self._sequence_compiling_with_kwargs([
            (self._get_curr_token_if_condition, {"expected_token": "do"}),
            (self._compile_subroutine_call, {}),
            (self._get_curr_token_if_condition, {"expected_token": ";"})
        ]
        )
        return self._add_elements(do_root, elements)

    def _compile_normal_subroutine_call(self) -> Union[List[Element], None]:

        # subroutineName '(' expressionList ')'
        return self._sequence_compiling_with_kwargs([
            (self._get_curr_token_if_condition, {"expected_type": TokenTypes.IDENTIFIER}),
            (self._get_curr_token_if_condition, {"expected_token": '('}),
            (self.compile_expression_list, {}),
            (self._get_curr_token_if_condition, {"expected_token": ')'})]
        )

    def _compile_class_subroutine_call(self) -> Union[List[Element], None]:
        # (className | varName) '.' subroutineName '(' expressionList ')'
        return self._sequence_compiling_with_kwargs([
            (self._get_curr_token_if_condition, {'expected_type': TokenTypes.IDENTIFIER}),
            (self._get_curr_token_if_condition, {'expected_token': '.'}),
            (self._get_curr_token_if_condition, {'expected_type': TokenTypes.IDENTIFIER}),
            (self._get_curr_token_if_condition, {'expected_token': '('}),
            (self.compile_expression_list, {}),
            (self._get_curr_token_if_condition, {'expected_token': ')'})

        ])

    def _compile_subroutine_call(self) -> Union[List[Element], None]:
        # normalSubroutineCall | classSubroutineCall
        return self._or_compiling([self._compile_normal_subroutine_call, self._compile_class_subroutine_call])

    def _compile_array_accessor(self) -> Union[List[Element], None]:
        return self._sequence_compiling_with_kwargs([
            (self._get_curr_token_if_condition, {"expected_token": "["}),
            (self.compile_expression, {}),
            (self._get_curr_token_if_condition, {"expected_token": "]"})
        ])

    def compile_let(self) -> Union[List[Element], None]:
        """Compiles a let statement."""
        # 'let' varName ('[' expression ']')? '=' expression ';'
        let_root = Element(LET_TAG)
        elements = self._sequence_compiling_with_kwargs([
            (self._get_curr_token_if_condition, {"expected_token": "let"}),
            (self._get_curr_token_if_condition, {"expected_type": TokenTypes.IDENTIFIER}),
            (self._question_mark_compiling, {"compile_method": self._compile_array_accessor}),
            (self._get_curr_token_if_condition, {"expected_token": "="}),
            (self.compile_expression, {}),
            (self._get_curr_token_if_condition, {"expected_token": ";"})
        ])
        return self._add_elements(let_root, elements)

    def compile_while(self) -> Union[List[Element], None]:
        """Compiles a while statement."""
        while_root = Element(WHILE_TAG)
        elements = self._sequence_compiling_with_kwargs([
            (self._get_curr_token_if_condition, {'expected_token': "while"}),
            (self._get_curr_token_if_condition, {'expected_token': "("}),
            (self.compile_expression, {}),
            (self._get_curr_token_if_condition, {'expected_token': ")"}),
            (self._get_curr_token_if_condition, {'expected_token': "{"}),
            (self.compile_statements, {}),
            (self._get_curr_token_if_condition, {'expected_token': "}"})
        ])
        return self._add_elements(while_root, elements)

    def compile_return(self) -> Union[List[Element], None]:
        """Compiles a return statement."""
        return_root = Element(RETURN_TAG)

        elements = self._sequence_compiling_with_kwargs([
            (self._get_curr_token_if_condition, {'expected_token': "return"}),
            (self._question_mark_compiling, {'compile_method': self.compile_expression}),
            (self._get_curr_token_if_condition, {'expected_token': ";"})
        ])

        return self._add_elements(return_root, elements)

    def _compile_else(self) -> Union[List[Element], None]:

        # ('else' '{' statements '}')
        return self._sequence_compiling_with_kwargs([
            (self._get_curr_token_if_condition, {"expected_token": "else"}),
            (self._get_curr_token_if_condition, {"expected_token": "{"}),
            (self.compile_statements, {}),
            (self._get_curr_token_if_condition, {"expected_token": "}"})])

    def compile_if(self) -> Union[List[Element], None]:
        """Compiles a if statement, possibly with a trailing else clause."""
        if_root = Element(IF_TAG)

        elements = self._sequence_compiling_with_kwargs([
            # 'if' '(' expression ')'
            (self._get_curr_token_if_condition, {'expected_token': "if"}),
            (self._get_curr_token_if_condition, {'expected_token': "("}),
            (self.compile_expression, {}),
            (self._get_curr_token_if_condition, {'expected_token': ")"}),

            # '{' statements '}'
            (self._get_curr_token_if_condition, {'expected_token': "{"}),
            (self.compile_statements, {}),
            (self._get_curr_token_if_condition, {'expected_token': "}"}),

            # ('else' '{' statements '}')?
            (self._question_mark_compiling, {'compile_method': self._compile_else})
        ])

        return self._add_elements(if_root, elements)

    def _compile_op(self) -> Union[List[Element], None]:
        return self.get_curr_token_if_one_of_conditions(expected_tokens=OPERATORS)

    def _compile_unary_op(self) -> Union[List[Element], None]:
        return self.get_curr_token_if_one_of_conditions(expected_tokens=UNARY_OPERATORS)

    def _compile_keyword_constant(self) -> Union[List[Element], None]:
        return self.get_curr_token_if_one_of_conditions(expected_tokens=KEYWORD_CONSTANTS)

    def _compile_op_term(self) -> Union[List[Element], None]:
        # op term
        return self._sequence_compiling([self._compile_op, self.compile_term])

    def compile_expression(self) -> Union[List[Element], None]:
        """Compiles an expression."""
        expression_root = Element(EXPRESSION_TAG)
        elements = self._sequence_compiling_with_kwargs([
            (self.compile_term, {}),
            (self._asterisk_compiling, {'compile_method': self._compile_op_term})
        ])
        return self._add_elements(expression_root, elements)

    def compile_term(self) -> Union[List[Element], None]:
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
        term_root = Element(TERM_TAG)
        next_token = self.tokenizer.next_token()
        if self.tokenizer.token_type() == TokenTypes.IDENTIFIER and next_token:
            if next_token == "[":
                elements = self._sequence_compiling_with_kwargs([
                    (self._get_curr_token_if_condition, {"expected_type": TokenTypes.IDENTIFIER}),
                    (self._get_curr_token_if_condition, {"expected_token": '['}),
                    (self.compile_expression, {}),
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
                    (self.compile_expression, {}),
                    (self._get_curr_token_if_condition, {"expected_token": ')'})
                ]),
                self._compile_callable_wrapper(self._sequence_compiling, [self._compile_unary_op, self.compile_term])
            ])
        return self._add_elements(term_root, elements)

    def _inner_compile_expression_list(self) -> List[Element]:
        # expression (',' expression)*
        return self._sequence_compiling_with_kwargs([
            (self.compile_expression, {}),
            (self._asterisk_compiling_with_args,
             {
                 "compile_method": self._sequence_compiling_with_kwargs,
                 "compile_methods_and_kwargs": [
                     (self._get_curr_token_if_condition, {"expected_token": ','},),
                     (self.compile_expression, {})
                 ]
             }
             )
        ])

    def compile_expression_list(self) -> List[Element]:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # (expression (',' expression)* )?
        expression_list_root = Element(EXPRESSION_LIST_TAG)
        elements = self._question_mark_compiling(self._inner_compile_expression_list)
        return self._add_elements(expression_list_root, elements)

    def compile_type(self) -> Union[List[Element], None]:
        return self.get_curr_token_if_one_of_conditions([None, None, None, TokenTypes.IDENTIFIER],
                                                        ["int", "char", "boolean", None])

    def compile_subroutine_body(self) -> Union[List[Element], None]:
        subroutine_body_root = Element(SUBROUTINE_TAG)
        elements = self._sequence_compiling_with_kwargs([
            (self._get_curr_token_if_condition, {'expected_token': "{"}),
            (self._asterisk_compiling, {'compile_method': self.compile_var_dec}),
            (self.compile_statements, {}),
            (self._get_curr_token_if_condition, {'expected_token': "}"})
        ])
        return self._add_elements(subroutine_body_root, elements)

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
