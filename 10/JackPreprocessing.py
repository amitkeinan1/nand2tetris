import re
from typing import List, Tuple

from jack_syntax import SYMBOLS, COMMENTS_REMOVING, STRING_CONST_PATTERN


def _remove_comments(text: str) -> str:
    for comment_regex, comment_replacement in COMMENTS_REMOVING.items():
        text = re.sub(comment_regex, comment_replacement, text)
    return text


def _clean_text(text: str) -> List[str]:
    text = _remove_comments(text)
    return text


def _remove_new_lines(text):
    return text.replace('\n', ' ')


def _remove_redundant_whitespaces(text):
    text = re.sub(' +', ' ', text)
    text = text.strip()
    return text


def _seperate_symbols(text: str) -> str:
    for symbol in SYMBOLS:
        text = text.replace(symbol, f" {symbol} ")
    return text


def _split_string_constants(jack_code: str) -> List[Tuple[str, bool]]:
    """
    split string constants from other code parts
    :param jack_code: jack code to handle
    :return: list of tuples. each tuple has code part and boolean value indicates whether it is a string constant.
    """
    code_parts = []
    string_const_indices = [m.span() for m in
                            re.finditer(STRING_CONST_PATTERN, jack_code)]  # find all string constants in jack code

    if len(string_const_indices) == 0:
        if jack_code == '':
            return []
        else:
            return [(jack_code, False)]

    first_start, first_end = string_const_indices[0]  # handle case where code does not start with a string
    if first_start != 0:
        code_parts.append((jack_code[:first_start], False))

    for i in range(len(string_const_indices) - 1):  # loop over all of the string constant matches
        start, end = string_const_indices[i]
        next_start = string_const_indices[i + 1][0]
        code_parts.append((jack_code[start: end], True))  # append the string constant
        code_parts.append((jack_code[end: next_start], False))  # append everything between string constants

    last_start, last_end = string_const_indices[-1]  # append the last string constant
    code_parts.append((jack_code[last_start: last_end], True))
    if last_end != len(jack_code):  # handle case where code does not end with a string
        code_parts.append((jack_code[last_end:], False))

    return code_parts


def _split_to_tokens(text):
    tokens = []
    code_parts = _split_string_constants(text)
    for code_part_text, is_string_constant in code_parts:
        if is_string_constant:
            part_tokens = [code_part_text]
        else:
            code_part_text = _seperate_symbols(code_part_text)
            code_part_text = _remove_new_lines(code_part_text)
            code_part_text = _remove_redundant_whitespaces(code_part_text)
            part_tokens = code_part_text.split()
        tokens += part_tokens
    return tokens


def get_tokens(jack_code: str) -> List[str]:
    """
    get text which is jack code and return the jack tokens in the code (ordered)
    :param jack_code: code to tokenize
    :return: jack tokens
    """
    jack_code = _clean_text(jack_code)
    tokens = _split_to_tokens(jack_code)
    return tokens


if __name__ == '__main__':
    with open("Square/Main.jack") as stream:
        text = stream.read()
        tokens = get_tokens(text)
        for token in tokens:
            print(token)
