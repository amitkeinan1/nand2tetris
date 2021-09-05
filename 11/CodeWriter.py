"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os

from lxml import etree
from lxml.etree import Element

from SymbolTable import SymbolTable
from VMWriter import VMWriter
from config import *
from jack_syntax import UNARY_OPERATORS
from xml_utils import get_text, get_type


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
        self.symbol_table = SymbolTable()  # TODO: remove symbol table (probably)
        self.vm_writer = VMWriter(open(output_path, 'w'))
        self.labels_count = 0
        self.class_var_count = 0
        self.class_name = None

    def write_code(self) -> None:
        """ the main compile class. uses compile_class for the logic and write the contents to a file."""
        self.write_class_code(self.parsed_code.getroot())
        self.vm_writer.close_output_stream()

    def write_class_code(self, class_xml: Element) -> None:
        """Compiles a complete class."""
        # 'class' className '{' classVarDec* subroutineDec* '}'
        self.class_name = get_text(class_xml[1])
        self.class_var_count = self._count_local_var_decs(class_xml, f"{CLASS_VAR_DEC_TAG}")
        for class_var in class_xml.findall(f"./{CLASS_VAR_DEC_TAG}"):
            self.write_class_var_dec_code(class_var)
        for subroutine_dec in class_xml.findall(f"./{SUBROUTINE_DEC_TAG}"):
            self.write_subroutine_dec_code(subroutine_dec, self.class_name)

    def _write_any_var_dec_code(self, var_dec: Element) -> None:
        for element in var_dec:
            element_type = get_type(element)
            element_name = get_text(element)
            if element_type.startswith("identifier"):
                category, index, status, var_type = self._get_identifier_details(element_type)
                if status == DEFINITION:
                    self.symbol_table.define(element_name, var_type, category)

    def write_class_var_dec_code(self, var_dec: Element) -> None:
        """Compiles a static declaration or a field declaration."""
        # ('static' | 'field') type varName (',' varName)* ';'
        self._write_any_var_dec_code(var_dec)

    def write_subroutine_dec_code(self, subroutine_dec: Element, class_name: str) -> None:
        """Compiles a complete method, function, or constructor."""
        # ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        subroutine_name = ".".join((class_name, get_text(subroutine_dec[2])))
        subroutine_type = get_text(subroutine_dec[0])
        self.write_parameter_list_code(subroutine_dec[4])
        self.vm_writer.write_function(subroutine_name,
                                      self._count_local_var_decs(subroutine_dec.find(SUBROUTINE_TAG), VAR_DEC_TAG))
        if subroutine_type == "constructor":
            self.vm_writer.write_push("CONST", self.class_var_count)
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("POINTER", 0)
        elif subroutine_type == "method":
            self.vm_writer.write_push("ARG", 0)
            self.vm_writer.write_pop("POINTER", 0)
        for var_dec in subroutine_dec.findall(f"./{SUBROUTINE_TAG}/{VAR_DEC_TAG}"):
            self.write_var_dec_code(var_dec)
            subroutine_dec.find("subroutineBody").find("statements")
        self.write_statements_code(subroutine_dec.find("subroutineBody").find(STATEMENTS_TAG))

    def write_parameter_list_code(self, param_list) -> None:
        # ((type varName) (',' type varName)*)?
        self._write_any_var_dec_code(param_list)

    def write_var_dec_code(self, var_dec: Element) -> None:
        """Compiles a var declaration."""
        # 'var' type varName (',' varName)* ';'
        self._write_any_var_dec_code(var_dec)

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

    def _handle_var_method(self, do_statement: Element, args_num: int):
        call_object = get_text(do_statement[1])
        segment = self._convert_kind_to_segment(self.symbol_table.kind_of(call_object))
        index = self.symbol_table.index_of(call_object)
        self.vm_writer.write_push(segment, index)
        call_object = self.symbol_table.type_of(call_object)
        function_name = call_object + "." + get_text(do_statement[3])
        return function_name, args_num + 1

    def _handle_other_class_method(self, do_statement: Element, args_num: int):
        call_object = get_text(do_statement[1])
        function_name = call_object + "." + get_text(do_statement[3])
        return function_name, args_num

    def _handle_curr_class_method(self, do_statement: Element, args_num: int, is_explicit):
        if is_explicit:
            call_object = get_text(do_statement[1])
            call_object = self.symbol_table.type_of(call_object)
        else:
            call_object = self.class_name

        self.vm_writer.write_push("POINTER", 0)

        if is_explicit:
            partial_method_name = get_text(do_statement[3])
        else:
            partial_method_name = get_text(do_statement[1])
        function_name = call_object + "." + partial_method_name

        return function_name, args_num + 1

    def write_do_code(self, do_statement: Element) -> None:
        """Compiles a do statement."""
        # 'do' subroutineCall ';'
        self._write_jack_code_as_comment(do_statement)
        args_num = len(do_statement.findall(f"./{EXPRESSION_LIST_TAG}/{EXPRESSION_TAG}"))

        if do_statement.findtext(SYMBOL_TAG, default="").strip() == ".":
            call_object = get_text(do_statement[1])
            if self.symbol_table.kind_of(call_object) is not None:  # if it is a var and not a class
                function_name, args_num = self._handle_var_method(do_statement, args_num)
            elif call_object == self.class_name:
                function_name, args_num = self._handle_curr_class_method(do_statement, args_num, is_explicit=True)
            else:
                function_name, args_num = self._handle_other_class_method(do_statement, args_num)
        else:
            function_name, args_num = self._handle_curr_class_method(do_statement, args_num, is_explicit=False)

        self.write_expression_list_code(do_statement.find(EXPRESSION_LIST_TAG))
        self.vm_writer.write_call(function_name, args_num)
        self.vm_writer.write_pop("TEMP", 0)

    def write_let_code(self, let_statement: Element) -> None:
        """Compiles a let statement."""
        # 'let' varName ('[' expression ']')? '=' expression ';'
        self._write_jack_code_as_comment(let_statement)
        expressions = let_statement.findall(EXPRESSION_TAG)
        var_elem = let_statement[1]
        right_expression = let_statement[-2]
        self.write_expression_code(right_expression)
        if len(expressions) > 1:
            var_kind, var_index, _, _, = self._get_identifier_details(get_type(var_elem))
            self.vm_writer.write_push(self._convert_kind_to_segment(var_kind), var_index)
            self.write_expression_code(let_statement[3])
            self.write_op("+")
            self.vm_writer.write_pop("POINTER", 1)
            self.vm_writer.write_pop("THAT", 0)
        else:
            category, index, status, var_type = self._get_identifier_details(get_type(var_elem))
            segment = self._convert_kind_to_segment(category)
            self.vm_writer.write_pop(segment, index)

    def write_while_code(self, while_statement: Element) -> None:
        """Compiles a while statement."""
        self.vm_writer.write_comment("while [yada yada yada]")

        start_label = self._generate_label("WHILE_EXP")
        out_label = self._generate_label("WHILE_END")

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
        self._write_jack_code_as_comment(return_statement)

        return_expression = return_statement.find(EXPRESSION_TAG)
        if return_expression is not None:
            self.write_expression_code(return_expression)
        else:
            self.vm_writer.write_push("CONST", 0)
        self.vm_writer.write_return()

    def write_if_code(self, if_statement: Element) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        false_label = self._generate_label("IF-FALSE")
        true_label = self._generate_label("IF-TRUE")
        statements = if_statement.findall(STATEMENTS_TAG)

        # !(cond):
        condition = if_statement.find(EXPRESSION_TAG)
        self._negate_and_push_condition(condition)

        self.vm_writer.write_if(false_label)  # if-goto L1
        self.write_statements_code(statements[0])  # execute s1
        self.vm_writer.write_goto(true_label)  # goto-L2
        self.vm_writer.write_label(false_label)  # label L1
        if len(statements) == 2:
            self.write_statements_code(statements[1])
        self.vm_writer.write_label(true_label)  # label L2

    def write_expression_code(self, expression: Element) -> None:
        """Compiles an expression."""
        self._write_jack_code_as_comment(expression)

        self.write_term_code(expression[0])
        for i in range(1, len(expression), 2):
            operator = expression[i]
            term = expression[i + 1]
            self.write_term_code(term)
            self.write_op(get_text(operator))

    def write_term_code(self, term: Element) -> None:
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
        if term.find(INTEGER_CONSTANT_TAG) is not None:  # integerConstant
            self.vm_writer.write_push("CONST", get_text(term[0]))

        elif term.find(STRING_CONSTANT_TAG) is not None:  # stringConstant
            string: str = get_text(term[0])
            self.vm_writer.write_push("CONST", len(string))
            self.vm_writer.write_call("String.new", 1)
            for char in string:
                self.vm_writer.write_push("CONST", ord(char))
                self.vm_writer.write_call("String.appendChar", 2)

        elif term.find(KEYWORD_CONSTANT_TAG) is not None:  # keyword
            self.write_keyword(get_text(term.find(KEYWORD_CONSTANT_TAG)))

        elif get_type(term[0]).startswith("identifier"):  # identifiers
            if len(term) == 1:  # varName
                var = term[0]
                var_kind, var_index, _, _, = self._get_identifier_details(var.tag)
                self.vm_writer.write_push(self._convert_kind_to_segment(var_kind), var_index)

            elif get_text(term[1]) == '[':  # varName '['expression']'
                array_elem = term[0]
                var_kind, var_index, _, _, = self._get_identifier_details(get_type(array_elem))
                self.vm_writer.write_push(self._convert_kind_to_segment(var_kind), var_index)
                self.write_expression_code(term.find(EXPRESSION_TAG))
                self.write_op("+")
                self.vm_writer.write_pop("POINTER", 1)
                self.vm_writer.write_push("THAT", 0)

            else:  # subroutineCall
                self.write_expression_list_code(term.find(EXPRESSION_LIST_TAG))
                args_num = len(term.findall(f"./{EXPRESSION_LIST_TAG}/{EXPRESSION_TAG}"))
                if term.findtext(SYMBOL_TAG).strip() == ".":
                    assert get_text(term[1]) == '.'
                    call_object = get_text(term[0])
                    if self.symbol_table.kind_of(call_object) is not None:  # if it is a var and not a class
                        call_object = self.symbol_table.type_of(call_object)
                    function_name = call_object + "." + get_text(term[2])

                else:
                    function_name = term[0]

                self.vm_writer.write_call(function_name, args_num)

        elif term.findtext(SYMBOL_TAG).strip() == "(":  # '('expression')'
            self.write_expression_code(term.find(EXPRESSION_TAG))

        elif term.findtext(SYMBOL_TAG).strip() in UNARY_OPERATORS:  # unaryOp term
            self.write_term_code(term.find(TERM_TAG))
            self.write_unary_op(term.findtext(SYMBOL_TAG).strip())

    def write_expression_list_code(self, expression_list: Element) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # (expression (',' expression)* )?
        for expression in expression_list.findall(EXPRESSION_TAG):
            self.write_expression_code(expression)

    def write_subroutine_body_code(self, subroutine: Element) -> None:
        for var_dec in subroutine.findall(VAR_DEC_TAG):
            self.write_var_dec_code(var_dec)
        self.write_statements_code(subroutine.find(STATEMENTS_TAG))

    def write_op(self, symbol: str):
        if symbol in op_to_vm_command.keys():
            self.vm_writer.write_arithmetic(op_to_vm_command[symbol])
        elif symbol in op_to_os_function.keys():
            self.vm_writer.write_call(op_to_os_function[symbol], 2)
        else:
            raise Exception("symbol is not operator")

    def write_unary_op(self, symbol: str):
        self.vm_writer.write_arithmetic(unary_op_to_vm_command[symbol])

    def write_keyword(self, keyword: str):
        if keyword == "true":
            self.vm_writer.write_push("CONST", 0)
            self.vm_writer.write_arithmetic("NOT")
        if keyword == "false":
            self.vm_writer.write_push("CONST", 0)
        if keyword == "null":  # TODO
            pass
        if keyword == "this":
            self.vm_writer.write_push("POINTER", 0)

    # helper methods
    def _generate_label(self, name: str) -> str:
        label = f"{name}-{self.labels_count}"
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

    @staticmethod
    def _convert_kind_to_segment(kind):
        return KIND_TO_SEGMENT[kind]

    def _write_jack_code_as_comment(self, elem):
        if os.environ.get("DEBUG"):
            self.vm_writer.write_comment(' '.join([get_text(e) for e in elem.iter() if e.text is not None]))
        pass

    @staticmethod
    def _is_var_dec(identifier_details):
        return identifier_details[2] == "definition"

    def _count_local_var_decs(self, elem: Element, var_tag):
        locals_count = 0
        var_decs = elem.findall(var_tag)
        for dec in var_decs:
            if dec.findtext(KEYWORD_CONSTANT_TAG).strip() == "static":
                continue
            locals_count += (len(list(filter(lambda x: x == ",", map(lambda elem: get_text(elem), dec)))) + 1)
        return locals_count


if __name__ == '__main__':
    file_name = "SquareMain"
    syntax_tree = etree.parse(f"amit_tests/{file_name}Extended.xml")
    code_writer = CodeWriter(syntax_tree, f"amit_tests/{file_name}VM.vm")
    code_writer.write_code()
