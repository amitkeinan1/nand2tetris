"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from typing import List, Callable, Tuple, Union

from lxml import etree
from lxml.etree import Element

from JackTokenizer import JackTokenizer
from config import TokenTypes
from jack_syntax import OPERATORS, UNARY_OPERATORS, KEYWORD_CONSTANTS


# TODO: there are two types of compile methods and inside the groups they all look the same, this s code duplication,
#  we can wrap the methods. update: I wrote sequence compiling and it solves much from the problem.

class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_path: str, output_path: str) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_path:
        :param output_path:
        """
        self.tokenizer = JackTokenizer(input_path)
        self.output_path = output_path

    # helper methods

    def _add_curr_token(self) -> Union[List[Element], None]:
        if self.tokenizer.curr_index == len(
                self.tokenizer.tokens):  # TODO: this is kinda patch but this is from the last stuff t fix, unless it causes bugs
            return None
        token_element = Element(self.tokenizer.token_type_repr())
        token_element.text = self.tokenizer.token_repr()
        self.tokenizer.advance()  # TODO: maybe sometimes we want to take it back? I think methods like compile_safely are the key
        return [token_element]

    def _add_token_if(self, expected_type=None, expected_token=None) -> Union[List[Element], None]:
        if self.tokenizer.curr_index == len(
                self.tokenizer.tokens):  # TODO: this is kinda patch but this is from the last stuff t fix, unless it causes bugs
            return None
        if (expected_type is None or self.tokenizer.token_type() == expected_type) and (
                expected_token is None or self.tokenizer.curr_token() == expected_token):
            return self._add_curr_token()
        else:
            return None

    def _add_token_if_or_compile(self, expected_type, expected_token, compile_method) -> Union[List[Element], None]:
        elements_to_add = self._add_token_if(expected_type, expected_token)
        if not elements_to_add:
            elements_to_add = compile_method()
        return elements_to_add

    def _add_token_if_or(self, expected_types=None, expected_tokens=None) -> Union[List[Element], None]:
        if expected_types is None and expected_tokens is None:
            raise ValueError("At least one of the arguments: expected_types and expected_tokens should not be None")
        if expected_types is not None and expected_tokens is not None and (len(expected_types) != len(expected_tokens)):
            raise ValueError("When providing both expected_types and expected_tokens they must have the same length")
        if expected_types is None:
            expected_types = [None for _ in range(len(expected_tokens))]
        if expected_tokens is None:
            expected_tokens = [None for _ in range(len(expected_types))]

        for expected_type, expected_token in zip(expected_types, expected_tokens):
            elements_to_add = self._add_token_if(expected_type, expected_token)  # TODO: make it "compile_safely"
            if elements_to_add:
                return elements_to_add
        return None

    def _compile_safely(self, compile_method: Callable):
        initial_token_index = self.tokenizer.curr_index
        res = compile_method()
        if not res:
            self.tokenizer.curr_index = initial_token_index
        return res

    def _or_compiling(self, compile_methods: List[Callable]) -> Union[List[Element], None]:
        for compile_method in compile_methods:
            curr_elements = self._compile_safely(compile_method)
            if curr_elements:
                return curr_elements
        return None

    def _asterisk_compiling(self, compile_method: Callable) -> List[Element]:
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
        curr_elements = self._compile_safely(compile_method)
        if curr_elements:
            return curr_elements
        else:
            return []

    def _sequence_compiling(self, compile_methods: List[Callable]) -> Union[List[Element], None]:
        elements_lists = [self._compile_safely(compile_method) for compile_method in compile_methods]
        if None not in elements_lists:
            return [elem for elements in elements_lists for elem in elements]
        else:
            return None

    def _sequence_compiling_with_kwargs(self, compile_methods_and_kwargs: List[Tuple[Callable, dict]]) -> List[Element]:
        compile_methods = [lambda: method_and_kwargs[0](**method_and_kwargs[1]) for method_and_kwargs in
                           compile_methods_and_kwargs]
        return self._sequence_compiling(compile_methods)

    def _add_elements(self, root: Element, elements: List[Element]) -> bool:
        if elements is None:
            return False
        for element in elements:
            root.append(element)
        return True

    # compile methods

    def compile_class(self) -> Union[List[Element], None]:  # TODO: this class should be normal compile method that
        # returns a list of elements and it should have a wrapper
        """Compiles a complete class."""
        class_root = Element("class")

        is_valid_class = True
        is_valid_class &= self._add_elements(class_root, self._add_token_if(TokenTypes.KEYWORD, "class"))
        is_valid_class &= self._add_elements(class_root, self._add_token_if(TokenTypes.IDENTIFIER))
        is_valid_class &= self._add_elements(class_root, self._add_token_if(TokenTypes.SYMBOL, "{"))
        is_valid_class &= self._add_elements(class_root, self._asterisk_compiling(self.compile_class_var_dec))
        is_valid_class &= self._add_elements(class_root, self._asterisk_compiling(self.compile_subroutine))
        is_valid_class &= self._add_elements(class_root, self._add_token_if(TokenTypes.SYMBOL, "}"))

        class_tree = etree.ElementTree(class_root)
        class_tree.write(self.output_path,
                         pretty_print=True)  # TODO: lxml cannot close and open empty elements and create new lines
        if is_valid_class:
            return [class_root]
        else:
            return None

    def compile_class_var_dec(self) -> Union[List[Element], None]:
        """Compiles a static declaration or a field declaration."""
        var_dec_root = Element("classVarDec")

        valid_var_dec = True
        valid_var_dec &= self._add_elements(var_dec_root, self._add_token_if_or(expected_tokens=["static", "field"]))
        valid_var_dec &= self._add_elements(var_dec_root, self.compile_type())
        valid_var_dec &= self._add_elements(var_dec_root, self._add_token_if(TokenTypes.IDENTIFIER))
        valid_var_dec &= self._add_elements(var_dec_root, self._asterisk_compiling(self._compile_comma_and_var_name))
        valid_var_dec &= self._add_elements(var_dec_root, self._add_token_if(expected_token=";"))

        if valid_var_dec:
            return [var_dec_root]
        else:
            return None

    def compile_subroutine(self) -> Union[List[Element], None]:
        """Compiles a complete method, function, or constructor."""
        subroutine_root = Element("subroutineDec")

        valid_subroutine = True
        valid_subroutine &= self._add_elements(subroutine_root, self._add_token_if_or(
            expected_tokens=["constructor", "function", "method"]))
        valid_subroutine &= self._add_elements(subroutine_root,
                                               self._add_token_if_or_compile(None, "void", self.compile_type))
        valid_subroutine &= self._add_elements(subroutine_root, self._add_token_if(TokenTypes.IDENTIFIER))
        valid_subroutine &= self._add_elements(subroutine_root, self._add_token_if(expected_token="("))
        valid_subroutine &= self._add_elements(subroutine_root, self.compile_parameter_list())
        valid_subroutine &= self._add_elements(subroutine_root, self._add_token_if(expected_token=")"))
        valid_subroutine &= self._add_elements(subroutine_root, self.compile_subroutine_body())

        if valid_subroutine:
            return [subroutine_root]
        else:
            return None

    def _inner_compile_parameter_list(self) -> Union[List[Element], None]:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        # (type varName) (',' type varName)*
        type_element = self.compile_type()
        var_name_element = self._add_token_if(expected_type=TokenTypes.IDENTIFIER)
        more_var_name_elements = self._asterisk_compiling(self._compile_comma_and_type_and_var_name)

        if type_element and var_name_element and more_var_name_elements:
            return type_element + var_name_element + more_var_name_elements
        else:
            return None

    def compile_parameter_list(self) -> Union[List[Element], None]:
        # ((type varName) (',' type varName)*)?
        parameter_list_root = Element("parameterList")
        self._add_elements(parameter_list_root, self._question_mark_compiling(self._inner_compile_parameter_list))
        return [parameter_list_root]

    def compile_var_dec(self) -> Union[List[Element], None]:
        """Compiles a var declaration."""
        # 'var' type varName (',' varName)* ';'
        var_dec_root = Element("varDec")
        valid_var_dec = True
        valid_var_dec &= self._add_elements(var_dec_root, self._add_token_if(expected_token="var"))
        valid_var_dec &= self._add_elements(var_dec_root, self.compile_type())
        valid_var_dec &= self._add_elements(var_dec_root, self._add_token_if(expected_type=TokenTypes.IDENTIFIER))
        valid_var_dec &= self._add_elements(var_dec_root,
                                            self._asterisk_compiling_with_args(self._sequence_compiling_with_kwargs,
                                                                               [(self._add_token_if,
                                                                                 {'expected_token': ','}),
                                                                                (self._add_token_if, {
                                                                                    'expected_type': TokenTypes.IDENTIFIER})]))
        valid_var_dec &= self._add_elements(var_dec_root, self._add_token_if(expected_token=";"))

        if valid_var_dec:
            return [var_dec_root]
        else:
            return None

    def compile_statement(self):
        return self._or_compiling(
            [self.compile_let, self.compile_if, self.compile_while, self.compile_do, self.compile_return])

    def compile_statements(self) -> List[Element]:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        statements_root = Element("statements")
        self._add_elements(statements_root, self._asterisk_compiling(self.compile_statement))
        return statements_root

    def compile_do(self) -> Union[List[Element], None]:
        """Compiles a do statement."""
        do_root = Element("doStatement")
        valid_do_statement = True
        valid_do_statement &= self._add_elements(do_root, self._add_token_if(expected_token="do"))
        valid_do_statement &= self._add_elements(do_root, self._compile_subroutine_call())

        if valid_do_statement:
            return [do_root]
        else:
            return None

    def _compile_normal_subroutine_call(self) -> Union[List[Element], None]:

        # subroutineName '(' expressionList ')'

        subroutine_name_element = self._add_token_if(expected_type=TokenTypes.IDENTIFIER)
        left_bracket_element = self._add_token_if(expected_token='(')
        expression_list_element = self.compile_expression_list()
        right_bracket_element = self._add_token_if(expected_token=')')

        if subroutine_name_element and left_bracket_element and expression_list_element + right_bracket_element:
            return subroutine_name_element + left_bracket_element + expression_list_element + right_bracket_element
        else:
            return None

    def _compile_class_subroutine_call(self) -> Union[List[Element], None]:

        # (className | varName) '.' subroutineName '(' expressionList ')'

        left_bracket_1_elements = self._add_token_if(expected_token='(')
        class_or_var_name_elements = self._add_token_if(expected_type=TokenTypes.IDENTIFIER)
        right_bracket_1_elements = self._add_token_if(expected_token=')')
        period_elements = self._add_token_if(expected_token='.')
        subroutine_name_elements = self._add_token_if(expected_type=TokenTypes.IDENTIFIER)
        left_bracket_2_elements = self._add_token_if(expected_token='(')
        expression_list_elements = self.compile_expression_list()
        right_bracket_2_elements = self._add_token_if(expected_token=')')

        elements_lists = [left_bracket_1_elements, class_or_var_name_elements, right_bracket_1_elements,
                          period_elements, subroutine_name_elements,
                          left_bracket_2_elements, expression_list_elements, right_bracket_2_elements]
        if not None in elements_lists:
            return [elem for elements in elements_lists for elem in elements]
        else:
            return None

    def _compile_subroutine_call(self) -> Union[List[Element], None]:
        # normalSubroutineCall | classSubroutineCall
        return self._or_compiling([self._compile_normal_subroutine_call, self._compile_class_subroutine_call])

    def _compile_array_accessor(self) -> Union[List[Element], None]:
        return self._sequence_compiling_with_kwargs([
            (self._add_token_if, {"expected_token": "["}),
            (self.compile_expression, {}),
            (self._add_token_if, {"expected_token": "]"})
        ])

    def compile_let(self) -> Union[List[Element], None]:
        """Compiles a let statement."""
        # 'let' varName ('[' expression ']')? '=' expression ';'
        let_root = Element("letStatement")
        valid_let_statement = True
        valid_let_statement &= self._add_elements(let_root, self._add_token_if(expected_token="let"))
        valid_let_statement &= self._add_elements(let_root, self._add_token_if(expected_type=TokenTypes.IDENTIFIER))
        valid_let_statement &= self._add_elements(let_root, self._question_mark_compiling(
            self._compile_array_accessor))
        valid_let_statement &= self._add_elements(let_root, self._add_token_if(expected_token="="))
        valid_let_statement &= self._add_elements(let_root, self.compile_expression())
        valid_let_statement &= self._add_elements(let_root, self._add_token_if(expected_token=";"))

        if valid_let_statement:
            return [let_root]
        else:
            return None

    def compile_while(self) -> Union[List[Element], None]:
        """Compiles a while statement."""
        while_root = Element("whileStatement")
        valid_while_statement = True
        valid_while_statement &= self._add_elements(while_root, self._add_token_if(expected_token="while"))
        valid_while_statement &= self._add_elements(while_root, self._add_token_if(expected_token="("))
        valid_while_statement &= self._add_elements(while_root, self.compile_expression())
        valid_while_statement &= self._add_elements(while_root, self._add_token_if(expected_token=")"))
        valid_while_statement &= self._add_elements(while_root, self._add_token_if(expected_token="{"))
        valid_while_statement &= self._add_elements(while_root, self.compile_statements())
        valid_while_statement &= self._add_elements(while_root, self._add_token_if(expected_token="}"))

        if valid_while_statement:
            return [while_root]
        else:
            return None

    def compile_return(self) -> Union[List[Element], None]:
        """Compiles a return statement."""
        return_root = Element("whileStatement")

        valid_return_statement = True
        valid_return_statement &= self._add_elements(return_root, self._add_token_if(expected_token="return"))
        valid_return_statement &= self._add_elements(return_root,
                                                     self._question_mark_compiling(self.compile_expression))
        valid_return_statement &= self._add_elements(return_root, self._add_token_if(expected_token=";"))

        if valid_return_statement:
            return [return_root]
        else:
            return None

    def _compile_else(self) -> Union[List[Element], None]:

        # ('else' '{' statements '}')
        else_elements = self._add_token_if(expected_token="else")
        left_bracket_elements = self._add_token_if(expected_token="{")
        statements_expression = self.compile_statements()
        right_bracket_elements = self._add_token_if(expected_token="}")

        if else_elements and left_bracket_elements and statements_expression and right_bracket_elements:
            return else_elements + left_bracket_elements + statements_expression + right_bracket_elements
        else:
            return None

    def compile_if(self) -> Union[List[Element], None]:
        """Compiles a if statement, possibly with a trailing else clause."""
        if_root = Element("ifStatement")

        valid_if_statement = True

        # 'if' '(' expression ')'
        valid_if_statement &= self._add_elements(if_root, self._add_token_if(expected_token="if"))
        valid_if_statement &= self._add_elements(if_root, self._add_token_if(expected_token="("))
        valid_if_statement &= self._add_elements(if_root, self.compile_expression())
        valid_if_statement &= self._add_elements(if_root, self._add_token_if(expected_token=")"))

        # '{' statements '}'
        valid_if_statement &= self._add_elements(if_root, self._add_token_if(expected_token="{"))
        valid_if_statement &= self._add_elements(if_root, self.compile_statement())
        valid_if_statement &= self._add_elements(if_root, self._add_token_if(expected_token="}"))

        # ('else' '{' statements '}')?
        valid_if_statement &= self._add_elements(if_root, self._question_mark_compiling(self._compile_else))

        if valid_if_statement:
            return [if_root]
        else:
            return None

    def _compile_op(self):
        return self._add_token_if_or(expected_tokens=OPERATORS)

    def _compile_unary_op(self):
        return self._add_token_if_or(expected_tokens=UNARY_OPERATORS)

    def _compile_keyword_constant(self):
        return self._add_token_if_or(expected_tokens=KEYWORD_CONSTANTS)

    def _compile_op_term(self):
        # op term
        op_elements = self._compile_op()
        term_elements = self.compile_term()

        if op_elements and term_elements:
            return op_elements + term_elements
        else:
            return None

    def compile_expression(self) -> Union[List[Element], None]:
        """Compiles an expression."""
        expression_root = Element("expression")

        valid_expression = True

        valid_expression &= self._add_elements(expression_root, self.compile_term())
        valid_expression &= self._add_elements(expression_root, self._asterisk_compiling(self._compile_op_term))

        if valid_expression:
            return [expression_root]
        else:
            return None

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
        return self._or_compiling([
            self._add_token_if(expected_type=TokenTypes.INT_CONST),
            self._add_token_if(expected_type=TokenTypes.STRING_CONST),
            self._compile_keyword_constant(),
            self._add_token_if(expected_type=TokenTypes.IDENTIFIER),
            self._sequence_compiling_with_kwargs([
                (self._add_token_if, {"expected_type": TokenTypes.IDENTIFIER}),
                (self._add_token_if, {"expected_token": '['}),
                (self.compile_expression, {}),
                (self._add_token_if, {"expected_token": ']'})
            ]),
            self._compile_subroutine_call,
            self._sequence_compiling_with_kwargs([
                (self._add_token_if, {"expected_token": '('}),
                (self.compile_expression, {}),
                (self._add_token_if, {"expected_token": ')'})
            ]),
            self._sequence_compiling_with_kwargs([(self._compile_unary_op, {}), (self.compile_term, {})])
            # TODO: can we handle recursion? NO
        ])

    def _inner_compile_expression_list(self) -> List[Element]:
        # expression (',' expression)*
        return self._sequence_compiling_with_kwargs([
            (self._add_token_if, {"expected_token": '('}),
            (self.compile_expression(), {}),
            self._asterisk_compiling_with_args(
                self._sequence_compiling_with_kwargs,
                [
                    (self._add_token_if, {"expected_token": ','},),
                    (self.compile_expression, {})
                ])
        ])

    def compile_expression_list(self) -> List[Element]:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # (expression (',' expression)* )?
        expression_list_root = Element("expressionList")
        self._add_elements(expression_list_root, self._question_mark_compiling(self._inner_compile_expression_list))
        return [expression_list_root]

    def compile_type(self) -> Union[List[Element], None]:
        return self._add_token_if_or([None, None, None, TokenTypes.IDENTIFIER], ["int", "char", "boolean", None])

    def compile_subroutine_body(self) -> Union[List[Element], None]:
        subroutine_body_root = Element("subroutineBody")

        valid_subroutine_body = True
        valid_subroutine_body &= self._add_elements(subroutine_body_root, self._add_token_if(expected_token="{"))
        valid_subroutine_body &= self._add_elements(subroutine_body_root,
                                                    self._asterisk_compiling(self.compile_var_dec))
        valid_subroutine_body &= self._add_elements(subroutine_body_root, self.compile_statements())
        valid_subroutine_body &= self._add_elements(subroutine_body_root, self._add_token_if(expected_token="}"))

        if valid_subroutine_body:
            return [subroutine_body_root]
        else:
            return None

    def _compile_comma_and_var_name(self) -> Union[List[Element], None]:
        comma_element = self._add_token_if(expected_token=",")
        var_name_element = self._add_token_if(expected_type=TokenTypes.IDENTIFIER)
        if comma_element and var_name_element:
            return comma_element + var_name_element
        return None

    def _compile_comma_and_type_and_var_name(self) -> Union[List[Element], None]:
        comma_element = self._add_token_if(expected_token=",")
        type_element = self.compile_type()
        var_name_element = self._add_token_if(expected_type=TokenTypes.IDENTIFIER)
        if comma_element and type_element and var_name_element:
            return comma_element + type_element + var_name_element
        return None
