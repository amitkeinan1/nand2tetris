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


# TODO: code duplication between compilation methods because of boolean inner var, we can wrap it

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

    def _add_curr_token(self) -> List[Element]:
        token_element = Element(self.tokenizer.token_type_repr())
        token_element.text = self.tokenizer.token_repr()
        self.tokenizer.advance()  # TODO: maybe sometimes we want to take it back?? but LL1 so maybe not
        return [token_element]

    def _add_token_if(self, expected_type=None, expected_token=None) -> List[Element]:
        if expected_type is None or self.tokenizer.token_type() == expected_type \
                and expected_token is None or self.tokenizer.curr_token() == expected_token:
            return self._add_curr_token()
        else:
            return None

    def _or_compiling(self, compile_methods) -> List[Element]:
        for compile_method in compile_methods:
            curr_elements = compile_method()
            if curr_elements:
                return curr_elements
        return None

    def _add_token_if_or_compile(self, expected_type, expected_token, compile_method) -> List[Element]:
        elements_to_add = self._add_token_if(expected_type, expected_token)
        if not elements_to_add:
            elements_to_add = compile_method()
        return elements_to_add

    def _add_token_if_or(self, expected_types=None, expected_tokens=None) -> List[Element]:
        if expected_types is None and expected_tokens is None:
            raise Exception("At least one of the arguments: expected_types and expected_tokens should not be None")
        if expected_types is None:
            expected_types = [None for _ in range(len(expected_tokens))]
        if expected_tokens is None:
            expected_tokens = [None for _ in range(len(expected_types))]

        for expected_type, expected_token in zip(expected_types, expected_tokens):
            elements_to_add = self._add_token_if(expected_type, expected_token)
            if elements_to_add:
                elements_to_add
        return None

    def _asterisk_compiling(self, compile_method) -> List[Element]:  # does not handle cases where it is not LL1
        elements = []
        curr_elements = compile_method()
        while curr_elements:
            elements += curr_elements
            curr_elements = compile_method()
        return elements

    def add_elements(self, root: Element, elements: List[Element]) -> bool:
        if elements is None:
            return False
        for element in elements:
            root.append(element)
        return True

    def compile_class(self) -> bool:
        """Compiles a complete class."""
        class_root = Element("class")

        is_valid_class = True
        is_valid_class &= self.add_elements(class_root, self._add_token_if("KEYWORD", "class"))
        is_valid_class &= self.add_elements(class_root, self._add_token_if("IDENTIFIER"))
        is_valid_class &= self.add_elements(class_root, self._add_token_if("SYMBOL", "{"))
        is_valid_class &= self.add_elements(class_root, self._asterisk_compiling(self.compile_class_var_dec))
        is_valid_class &= self.add_elements(class_root, self._asterisk_compiling(self.compile_subroutine))
        is_valid_class &= self.add_elements(class_root, self._add_token_if("SYMBOL", "{"))

        class_tree = etree.ElementTree(class_root)
        class_tree.write(self.output_path, pretty_print=True)

    def compile_class_var_dec(self) -> List[Element]:
        """Compiles a static declaration or a field declaration."""
        var_dec_root = Element("classVarDec")

        valid_var_dec = True
        valid_var_dec &= self.add_elements(var_dec_root, self._add_token_if_or(expected_tokens=["static", "field"]))
        valid_var_dec &= self.add_elements(var_dec_root, self.compile_type())
        valid_var_dec &= self.add_elements(var_dec_root, self._add_token_if("IDENTIFIER"))
        # TODO: add multiple commas
        valid_var_dec &= self.add_elements(var_dec_root, self._add_token_if(expected_token=";"))

        if valid_var_dec:
            return [var_dec_root]
        else:
            return None

    def compile_subroutine(self) -> List[Element]:
        """Compiles a complete method, function, or constructor."""
        subroutine_root = Element("subroutineDec")

        valid_subroutine = True
        valid_subroutine &= self.add_elements(subroutine_root, self._add_token_if_or(
            expected_tokens=["constructor", "function", "method"]))
        valid_subroutine &= self.add_elements(subroutine_root,
                                              self._add_token_if_or_compile(None, "void", self.compile_type))
        valid_subroutine &= self.add_elements(subroutine_root, self._add_token_if("IDENTIFIER"))
        valid_subroutine &= self.add_elements(subroutine_root, self._add_token_if(expected_token="("))
        valid_subroutine &= self.add_elements(subroutine_root, self.compile_parameter_list())
        valid_subroutine &= self.add_elements(subroutine_root, self._add_token_if(expected_token=")"))
        valid_subroutine &= self.add_elements(subroutine_root, self.compile_subroutine_body())

        if valid_subroutine:
            return [subroutine_root]
        else:
            return None

    def compile_parameter_list(self) -> bool:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        return []  # TODO: write method

    def compile_var_dec(self) -> bool:
        """Compiles a var declaration."""
        pass

    def compile_statements(self) -> bool:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # Your code goes here!
        pass

    def compile_do(self) -> bool:
        """Compiles a do statement."""
        # Your code goes here!
        pass

    def compile_let(self) -> bool:
        """Compiles a let statement."""
        # Your code goes here!
        pass

    def compile_while(self) -> bool:
        """Compiles a while statement."""
        # Your code goes here!
        pass

    def compile_return(self) -> bool:
        """Compiles a return statement."""
        # Your code goes here!
        pass

    def compile_if(self) -> bool:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        pass

    def compile_expression(self) -> bool:
        """Compiles an expression."""
        # Your code goes here!
        pass

    def compile_term(self) -> bool:
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
        pass

    def compile_expression_list(self) -> bool:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        pass

    def compile_type(self) -> List[Element]:
        return self._add_token_if_or([None, None, None, "IDENTIFIER"], ["int", "char", "boolean", None])

    def compile_subroutine_body(self):
        return []  # TODO: add method
