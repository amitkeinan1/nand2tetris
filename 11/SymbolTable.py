"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Symbol:
    name: str
    symbol_type: str
    kind: str
    index: int


CLASS_SCOPE = "class"
SUBROUTINE_SCOPE = "subroutine"
SUBROUTINES = "subroutine_dec"

FIELD_KIND = "FIELD"
STATIC_KIND = "STATIC"
VAR_KIND = "VAR"
ARG_KIND = "ARG"
CONSTRUCTOR_KIND = "constructor"
FUNCTION_KIND = "function"
METHOD_KIND = "method"
CLASS_KINDS = {FIELD_KIND, STATIC_KIND}
SUBROUTINE_LOCALS_KINDS = {VAR_KIND, ARG_KIND}
SUBROUTINE_KINDS = {CONSTRUCTOR_KIND, FUNCTION_KIND, METHOD_KIND}
RESOLUTION_ORDER = [SUBROUTINE_SCOPE, CLASS_SCOPE, SUBROUTINES]


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self._table = {CLASS_SCOPE: {}, SUBROUTINE_SCOPE: {}, SUBROUTINES: {}}
        self._kind_indexes = {FIELD_KIND: 0, STATIC_KIND: 0, VAR_KIND: 0, ARG_KIND: 0, CONSTRUCTOR_KIND: 0,
                              FUNCTION_KIND: 0, METHOD_KIND: 0}

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self._table[SUBROUTINE_SCOPE] = {}
        for kind in SUBROUTINE_LOCALS_KINDS:
            self._kind_indexes[kind] = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        symbol_index = self.var_count(kind)
        self._kind_indexes[kind] += 1
        symbol = Symbol(name, type, kind, symbol_index)
        if kind in CLASS_KINDS:
            self._table[CLASS_SCOPE][name] = symbol
        elif kind in SUBROUTINE_LOCALS_KINDS:
            self._table[SUBROUTINE_SCOPE][name] = symbol
        elif kind in SUBROUTINE_KINDS:
            self._table[SUBROUTINES][name] = symbol

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in
            the current scope.
        """
        return self._kind_indexes[kind]

    def kind_of(self, name: str) -> Optional[str]:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        for scope in RESOLUTION_ORDER:
            symbol: Symbol = self._table[scope].get(name)
            if symbol is not None:
                return symbol.kind
        return

    def type_of(self, name: str) -> Optional[str]:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        for scope in RESOLUTION_ORDER:
            symbol: Symbol = self._table[scope].get(name)
            if symbol is not None:
                return symbol.symbol_type
        return

    def index_of(self, name: str) -> Optional[int]:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        for scope in RESOLUTION_ORDER:
            symbol: Symbol = self._table[scope].get(name)
            if symbol is not None:
                return symbol.index
        return
