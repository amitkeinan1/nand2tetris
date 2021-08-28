import re
import typing
from typing import List, Tuple

from config import INLINE_COMMENT_SIGN


def _remove_inline_comments(line: str) -> str:
    return line.split(INLINE_COMMENT_SIGN)[0]


def _clean_lines(lines: List[str]) -> List[str]:
    return list(map(_remove_inline_comments, lines))


def _remove_comments(text: str) -> str:
    text = re.sub("//.*\n", "\n", text)  # remove // inline comments
    text = re.sub("/\*.*\*/", "", text)  # remove /* this kind of    comments */
    text = re.sub("/\*\*.*\*/", "", text)  # remove /** api comments */
    return text


# def _remove_multiple_whitespaces(text):
#     return re.sub(' +', ' ', text)

def _is_line_not_whitespace(line: str):
    return line != ''


def _remove_whitespace_lines(lines):
    return list(filter(_is_line_not_whitespace, lines))


def _get_clean_lines(text: str) -> List[str]:
    text = _remove_comments(text)
    # lines = [line.strip() for line in text.splitlines()]
    # lines = _remove_whitespace_lines(lines)
    return text


# def _seperate_symbols(text: str) -> str:
#     for symbol in SYMBOLS:
#         text = text.replace(symbol, f" {symbol} ")
#     text = _remove_multiple_whitespaces(text)
#     return text


def preprocess_jack_code(stream: typing.TextIO):
    text = stream.read()
    text = _get_clean_lines(text)
    return text


def split_strings_constants(jack_code: str) -> List[Tuple[str, bool]]:
    """
    split string constants from other code parts
    :param jack_code: jack code to handle
    :return: list of tuples. each tuple has code part and boolean value indicates whether it is a string constant.
    """
    parts = []
    string_const_indices = [m.span() for m in
                            re.finditer('"[^\\n]*?"', jack_code)]  # find all string constants in jack code

    first_start, first_end = string_const_indices[0]  # handle case where code does not start with a string
    if first_start != 0:
        parts.append((jack_code[:first_start], False))

    for i in range(len(string_const_indices) - 1):  # loop over all of the string constant matches
        start, end = string_const_indices[i]
        next_start = string_const_indices[i + 1][0]
        parts.append((jack_code[start: end], True))  # append the string constant
        parts.append((jack_code[end: next_start], False))  # append everything between string constants

    last_start, last_end = string_const_indices[-1]  # append the last string constant
    parts.append((jack_code[last_start: last_end], True))
    if last_end != len(jack_code):  # handle case where code does not end with a string
        parts.append((jack_code[last_end:], False))

    return parts


if __name__ == '__main__':
    with open("Square/Main.jack") as stream:
        text = preprocess_jack_code(stream)
        # print(text)
        parts = split_strings_constants(text)
        print(parts)
