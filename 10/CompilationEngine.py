"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from lxml import etree

from JackTokenizer import JackTokenizer
from config import TokenTypes

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

    def _add_curr_token(self, root):
        etree.SubElement(root, self.tokenizer.token_type_repr()).text = self.tokenizer.token_repr()
        self.tokenizer.advance()

    def _add_token_if(self, root, expected_type=None, expected_token=None) -> bool:
        if expected_type is None or self.tokenizer.token_type() == expected_type \
                and expected_token is None or self.tokenizer.curr_token() == expected_token:
            self._add_curr_token(root)
            return True
        else:
            return False

    def _add_token_if_or_compile(self, root, expected_type, expected_token, compile_method):
        did_add_token = self._add_token_if(root, expected_type, expected_token)
        if not did_add_token:
            did_add_token = compile_method(root)
        return did_add_token

    def _add_token_if_or(self, root, expected_types=None, expected_tokens=None) -> bool:
        if expected_types is None and expected_tokens is None:
            raise ValueError("At least one of the arguments: expected_types and expected_tokens should not be None")
        if expected_types is not None and expected_tokens is not None and (len(expected_types) != len(expected_tokens)):
            raise ValueError("When providing both expected_types and expected_tokens they must have the same length")
        if expected_types is None:
            expected_types = [None for _ in range(len(expected_tokens))]
        if expected_tokens is None:
            expected_tokens = [None for _ in range(len(expected_types))]

        for expected_type, expected_token in zip(expected_types, expected_tokens):
            did_add_token = self._add_token_if(root, expected_type, expected_token)
            if did_add_token:
                return True
        return False

    def _compile_multiple(self, root, compile_method) -> bool:  # does not handle cases where it is not LL1
        compile_success = compile_method(root)
        while compile_success:
            compile_method(root)
        return True

    def compile_class(self) -> bool:
        """Compiles a complete class."""
        class_root = etree.Element("class")

        self._add_token_if(class_root, "KEYWORD", "class")
        self._add_token_if(class_root, "IDENTIFIER")
        self._add_token_if(class_root, "SYMBOL", "{")
        self.compile_class_var_dec(class_root)  # TODO: maybe multiple
        self.compile_subroutine(class_root)  # TODO: maybe multiple
        self._add_token_if(class_root, "SYMBOL", "{")
        class_tree = etree.ElementTree(class_root)

        class_tree.write(self.output_path, pretty_print=True)

    def compile_class_var_dec(self, root) -> bool:
        """Compiles a static declaration or a field declaration."""
        var_dec_root = etree.SubElement(root, "classVarDec")

        self._add_token_if_or(var_dec_root, expected_tokens=["static", "field"])
        self.compile_type(var_dec_root)
        self._add_token_if(var_dec_root, "IDENTIFIER")
        # TODO: add multiple commas
        self._add_token_if(var_dec_root, expected_token=";")

    def compile_subroutine(self, root) -> bool:
        """Compiles a complete method, function, or constructor."""
        subroutine_root = etree.SubElement(root, "subroutineDec")

        self._add_token_if_or(subroutine_root, expected_tokens=["constructor", "function", "method"])
        self._add_token_if_or_compile(subroutine_root, None, "void", self.compile_type)
        self._add_token_if(subroutine_root, TokenTypes.IDENTIFIER)
        self._add_token_if(subroutine_root, expected_token="(")
        self.compile_parameter_list(subroutine_root)
        self._add_token_if(subroutine_root, expected_token=")")
        self.compile_subroutine_body(subroutine_root)

    def compile_parameter_list(self) -> bool:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # Your code goes here!
        pass

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

    def compile_type(self, root) -> bool:
        return self._add_token_if_or(root, [None, None, None, TokenTypes.IDENTIFIER], ["int", "char", "boolean", None])

    def compile_subroutine_body(self, root):
        pass
