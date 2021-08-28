import re
import typing
from typing import List

INLINE_COMMENT_SIGN = "//"


def _remove_inline_comments(line: str) -> str:
    return line.split(INLINE_COMMENT_SIGN)[0]


def _clean_lines(lines: List[str]) -> List[str]:
    return list(map(_remove_inline_comments, lines))


def _remove_comments(text: str) -> str:
    text = re.sub("/\*.*\*/", "", text)  # remove /* this kind of    comments */
    text = re.sub("/\*\*.*\*/", "", text)  # remove /** api comments */
    return text


def _clean_text(text: str) -> str:
    text = _remove_comments(text)
    text = re.sub(' +', ' ', text)
    return text


def read_jack_code(stream: typing.TextIO):
    lines = stream.read().splitlines()
    lines = _clean_lines(lines)
    text = ' '.join(lines)
    text = _clean_text(text)
    return text


if __name__ == '__main__':
    with open("Square/Main.jack") as stream:
        print(read_jack_code(stream))
