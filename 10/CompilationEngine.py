"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from typing import List
from lxml import etree
from lxml.etree import Element
from JackTokenizer import JackTokenizer
from config import TokenTypes
from jack_syntax import OPERATORS


# TODO: there are two types of compile methods and inside the groups they all look the same, this s code duplication,
#  we can wrap the methods

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

    def _add_curr_token(self) -> List[Element]:
        if self.tokenizer.curr_index == len(
                self.tokenizer.tokens):  # TODO: this is kinda patch but this is from the last stuff t fix, unless it causes bugs
            return None
        token_element = Element(self.tokenizer.token_type_repr())
        token_element.text = self.tokenizer.token_repr()
        self.tokenizer.advance()  # TODO: maybe sometimes we want to take it back? I think methods like compile_safely are the key
        return [token_element]

    def _add_token_if(self, expected_type=None, expected_token=None) -> List[Element]:
        if self.tokenizer.curr_index == len(
                self.tokenizer.tokens):  # TODO: this is kinda patch but this is from the last stuff t fix, unless it causes bugs
            return None
        if (expected_type is None or self.tokenizer.token_type() == expected_type) and (
                expected_token is None or self.tokenizer.curr_token() == expected_token):
            return self._add_curr_token()
        else:
            return None

    def _add_token_if_or_compile(self, expected_type, expected_token, compile_method) -> List[Element]:
        elements_to_add = self._add_token_if(expected_type, expected_token)
        if not elements_to_add:
            elements_to_add = compile_method()
        return elements_to_add

    def _add_token_if_or(self, expected_types=None, expected_tokens=None) -> List[Element]:
        if expected_types is None and expected_tokens is None:
            raise ValueError("At least one of the arguments: expected_types and expected_tokens should not be None")
        if expected_types is not None and expected_tokens is not None and (len(expected_types) != len(expected_tokens)):
            raise ValueError("When providing both expected_types and expected_tokens they must have the same length")
        if expected_types is None:
            expected_types = [None for _ in range(len(expected_tokens))]
        if expected_tokens is None:
            expected_tokens = [None for _ in range(len(expected_types))]

        for expected_type, expected_token in zip(expected_types, expected_tokens):
            # elements_to_add = self._add_token_if(expected_type, expected_token)  # TODO: make it "compile_safely"
            if elements_to_add:
                return elements_to_add
        return None

    def _compile_safely(self, compile_method):
        initial_token_index = self.tokenizer.curr_index
        res = compile_method()
        if not res:
            self.tokenizer.curr_index = initial_token_index
        return res

    def _or_compiling(self, compile_methods) -> List[Element]:
        for compile_method in compile_methods:
            curr_elements = self._compile_safely(compile_method)
            if curr_elements:
                return curr_elements
        return None

    def _asterisk_compiling(self, compile_method) -> List[Element]:
        elements = []
        curr_elements = self._compile_safely(compile_method)
        while curr_elements:
            elements += curr_elements
            curr_elements = self._compile_safely(compile_method)

        return elements

    def _question_mark_compiling(self, compile_method) -> List[Element]:
        curr_elements = self._compile_safely(compile_method)
        if curr_elements:
            return curr_elements
        else:
            return []

    def _add_elements(self, root: Element, elements: List[Element]) -> List[Element]:
        if elements is None:
            return False
        for element in elements:
            root.append(element)
        return True

    # compile methods

    def compile_class(self) -> List[Element]:  # TODO: it should return elements
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

    def compile_class_var_dec(self) -> List[Element]:
        """Compiles a static declaration or a field declaration."""
        var_dec_root = Element("classVarDec")

        valid_var_dec = True
        valid_var_dec &= self._add_elements(var_dec_root, self._add_token_if_or(expected_tokens=["static", "field"]))
        valid_var_dec &= self._add_elements(var_dec_root, self.compile_type())
        valid_var_dec &= self._add_elements(var_dec_root, self._add_token_if(TokenTypes.IDENTIFIER))
        valid_var_dec &= self._add_elements(var_dec_root, self._asterisk_compiling(self.compile_comma_and_var_name))
        valid_var_dec &= self._add_elements(var_dec_root, self._add_token_if(expected_token=";"))

        if valid_var_dec:
            return [var_dec_root]
        else:
            return None

    def compile_subroutine(self) -> List[Element]:
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

    def _inner_compile_parameter_list(self) -> List[Element]:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        type_element = self.compile_type()
        var_name_element = self._add_token_if(expected_type=TokenTypes.IDENTIFIER)
        more_var_name_elements = self._asterisk_compiling(self.compile_comma_and_type_and_var_name)

        if type_element and var_name_element and more_var_name_elements:
            return type_element + var_name_element + more_var_name_elements
        else:
            return None

    def compile_parameter_list(self) -> List[Element]:
        parameter_list_root = Element("parameterList")
        self._add_elements(parameter_list_root, self._question_mark_compiling(self._inner_compile_parameter_list))
        return [parameter_list_root]

    def compile_var_dec(self) -> List[Element]:
        """Compiles a var declaration."""

        var_dec_root = Element("varDec")
        valid_var_dec = True
        valid_var_dec &= self._add_elements(var_dec_root, self._add_token_if(expected_token="var"))
        valid_var_dec &= self._add_elements(var_dec_root, self.compile_type())
        valid_var_dec &= self._add_elements(var_dec_root, self._add_elements(var_dec_root,
                                                                             self._asterisk_compiling(
                                                                                 self.compile_comma_and_type_and_var_name)))
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
        self._add_elements(self._asterisk_compiling(self.compile_statement()))
        return statements_root

    def compile_do(self) -> List[Element]:
        """Compiles a do statement."""
        do_root = Element("doStatement")
        valid_do_statement = True
        valid_do_statement &= self._add_elements(do_root, self._add_token_if(expected_token="do"))
        valid_do_statement &= self._add_elements(do_root, self._compile_subroutine_call())

        if valid_do_statement:
            return [do_root]
        else:
            return None

    def _compile_subroutine_call(self) -> List[Element]:
        # TODO
        pass

    def _compile_array_accessor(self) -> List[Element]:
        left_bracket_element = self._add_token_if(expected_token="[")
        expression_element = self.compile_expression()
        right_bracket_element = self._add_token_if(expected_token="]")
        if left_bracket_element and expression_element and right_bracket_element:
            return [left_bracket_element, expression_element, right_bracket_element]
        return None

    def compile_let(self) -> List[Element]:
        """Compiles a let statement."""
        let_root = Element("letStatement")
        valid_let_statement = True
        valid_let_statement &= self._add_elements(let_root, self._add_token_if(expected_token="let"))
        valid_let_statement &= self._add_elements(let_root, self._compile_array_accessor())  # TODO: make optional
        valid_let_statement &= self._add_elements(let_root, self._add_token_if(expected_token="="))
        valid_let_statement &= self._add_elements(let_root, self.compile_expression())
        valid_let_statement &= self._add_elements(let_root, self._add_token_if(expected_token=";"))

        if valid_let_statement:
            return [let_root]
        else:
            return None

    def compile_while(self) -> List[Element]:
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

    def compile_return(self) -> List[Element]:
        """Compiles a return statement."""
        return_root = Element("whileStatement")

        valid_return_statement = True
        valid_return_statement &= self._add_elements(return_root, self._add_token_if(expected_token="return"))
        valid_return_statement &= self._add_elements(return_root,
                                                     self._question_mark_compiling(self.compile_expression()))
        valid_return_statement &= self._add_elements(return_root, self._add_token_if(expected_token=";"))

        if valid_return_statement:
            return [return_root]
        else:
            return None

    def _compile_else(self) -> List[Element]:

        # ('else' '{' statements '}')
        else_elements = self._add_token_if(expected_token="else")
        left_bracket_elements = self._add_token_if(expected_token="{")
        statements_expression = self.compile_statements()
        right_bracket_elements = self._add_token_if(expected_token="}")

        if else_elements and left_bracket_elements and statements_expression and right_bracket_elements:
            return else_elements + left_bracket_elements + statements_expression + right_bracket_elements
        else:
            return None

    def compile_if(self) -> List[Element]:
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

    def _compile_op_term(self):
        # op term
        op_elements = self._compile_op()
        term_elements = self.compile_term()

        if op_elements and term_elements:
            return op_elements + term_elements
        else:
            return None

    def compile_expression(self) -> List[Element]:
        """Compiles an expression."""
        expression_root = Element("expression")

        valid_expression = True

        valid_expression &= self._add_elements(expression_root, self.compile_term())
        valid_expression &= self._add_elements(expression_root, self._asterisk_compiling(self._compile_op_term))

        if valid_expression:
            return [expression_root]
        else:
            return None

    def compile_term(self) -> List[Element]:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!
        # TODO
        pass

    def compile_expression_list(self) -> List[Element]:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        # TODO
        pass

    def compile_type(self) -> List[Element]:
        return self._add_token_if_or([None, None, None, TokenTypes.IDENTIFIER], ["int", "char", "boolean", None])

    def compile_subroutine_body(self) -> List[Element]:
        subroutine_body_root = Element("subroutineBody")

        valid_subroutine_body = True
        valid_subroutine_body &= self._add_elements(subroutine_body_root, self._add_token_if(expected_token="{"))
        valid_subroutine_body &= self._add_elements(subroutine_body_root,
                                                    self._asterisk_compiling(self.compile_var_dec()))
        valid_subroutine_body &= self._add_elements(subroutine_body_root,
                                                    self._asterisk_compiling(self.compile_statements()))
        valid_subroutine_body &= self._add_elements(subroutine_body_root, self._add_token_if(expected_token="}"))

        if valid_subroutine_body:
            return [subroutine_body_root]
        else:
            return None

    def compile_comma_and_var_name(self) -> List[Element]:
        comma_element = self._add_token_if(expected_token=",")
        var_name_element = self._add_token_if(expected_type=TokenTypes.IDENTIFIER)
        if comma_element and var_name_element:
            return comma_element + var_name_element
        return None

    def compile_comma_and_type_and_var_name(self) -> List[Element]:
        comma_element = self._add_token_if(expected_token=",")
        type_element = self.compile_type()
        var_name_element = self._add_token_if(expected_type=TokenTypes.IDENTIFIER)
        if comma_element and type_element and var_name_element:
            return comma_element + type_element + var_name_element
        return None


if __name__ == '__main__':
    root = Element("root")
    c = CompilationEngine("Amit/Main.jack", "Amit/Main.xml")
    c._add_elements(root, c.compile_subroutine_body())
    class_tree = etree.ElementTree(root)
    class_tree.write(c.output_path, pretty_print=True)
