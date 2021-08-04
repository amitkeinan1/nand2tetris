"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from tables import dest_table, jump_table, comp_table


class Code:
    """Translates Hack assembly language mnemonics into binary codes."""

    @staticmethod
    def dest(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a dest mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """

        return dest_table[mnemonic]

    @staticmethod
    def comp(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a comp mnemonic string.

        Returns:
            str: 9-bit long binary code of the given mnemonic.
        """
        if "M" in mnemonic:
            a = "1"
            dummy_mnemonic = mnemonic.replace("M", "B")
        else:
            a = "0"
            dummy_mnemonic = mnemonic.replace("D", "B")
        return f"11{a}{comp_table[dummy_mnemonic]}"

    @staticmethod
    def jump(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a jump mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        return jump_table[mnemonic]

    @staticmethod
    def translate_a_command(value: str):
        binary_value = '{0:015b}'.format(int(value))
        return f"0{binary_value}"

    @staticmethod
    def translate_c_command(dest, comp, jump):
        bin_dest, bin_comp, bin_jump = dest(dest), comp(comp), ump(jump)
        return f"1{bin_comp}{bin_dest}{bin_jump}"



