#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   Copyright 2017 Kaede Hoshikawa
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from typing import List, Optional, Sequence, Type

from . import printer
from . import exceptions

import abc
import re

__all__ = ["Statement", "Root", "Block", "BaseOutput", "builtin_stmt_classes"]

_VALID_FN_NAME_RE = re.compile(r"^[a-zA-Z]([a-zA-Z0-9\_]+)?$")


def _is_valid_fn_name(maybe_fn_name: str) -> bool:
    """
    Check if this is a valid function name.
    """
    return (re.fullmatch(_VALID_FN_NAME_RE, name) is not None)


class Statement(abc.ABC):
    def append_stmt(self, stmt: "Statement") -> None:
        raise NotImplementedError

    @abc.abstractmethod
    @property
    def should_indent(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    @property
    def should_append(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    @property
    def should_unindent(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    @property
    def line_no(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        raise NotImplementedError

    @abc.abstractmethod
    def print_code(self, code_printer: printer.CodePrinter) -> None:
        raise NotImplementedError


class Root(Statement):
    def __init__(self, filepath: str) -> None:
        self._filepath = filepath

        self._stmts: List[Statement] = []

    def append_stmt(self, stmt: Statement) -> None:
        self._stmts.append(stmt)

    def append_block(self, block: "Block") -> None:
        raise NotImplementedError

    @property
    def should_indent(self) -> bool:
        raise NotImplementedError("This does not apply to Root.")

    @property
    def should_append(self) -> bool:
        raise NotImplementedError("This does not apply to Root.")

    @property
    def should_unindent(self) -> bool:
        raise NotImplementedError("This does not apply to Root.")

    @property
    def line_no(self) -> int:
        raise NotImplementedError("This does not apply to Root.")

    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        raise NotImplementedError("This does not apply to Root.")

    def print_code(self, code_printer: printer.CodePrinter) -> None:
        raise NotImplementedError


class Block(Statement):
    def __init__(self, block_name: str, filepath: str, line_no: int) -> None:
        self._block_name = block_name
        self._filepath = filepath
        self._line_no = line_no

    @property
    def block_name(self):
        return self._block_name

    @property
    def should_indent(self) -> bool:
        return True

    @property
    def should_append(self) -> bool:
        return True

    @property
    def should_unindent(self) -> bool:
        return False

    @property
    def line_no(self) -> int:
        return self._line_no

    @abc.abstractmethod
    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        splitted_stmt = stmt_str.split(" ", 1)
        if splitted_stmt[0] != "block":
            return None

        if len(splitted_stmt) != 2 or (not splitted_stmt[1].strip()):
            raise exceptions.TemplateSyntaxError(
                "Block name cannot be empty.")

        block_name = splitted_stmt[1].strip()

        if not _is_valid_fn_name(block_name):
            raise exceptions.TemplateSyntaxError(
                "Invalid Block Statement. Block name expected, got: {}."
                .format(repr(block_name)))

        return Cls(
            block_name=block_name,
            filepath=filepath, line_no=line_no)


class Plain(Statement):
    def __init__(self, stmt_str: str) -> None:
        self._stmt_str = stmt_str

    @property
    def should_indent(self) -> bool:
        return False

    @property
    def should_append(self) -> bool:
        return True

    @property
    def should_unindent(self) -> bool:
        return False

    @property
    def line_no(self) -> int:
        raise NotImplementedError("This does not apply to Plain.")

    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        raise NotImplementedError("This does not apply to Plain.")

    def print_code(self, code_printer: printer.CodePrinter) -> None:
        raise NotImplementedError


class BaseOutput(Statement):
    _filter_fn_names: List[str] = []

    def __init__(
        self, output_filter: str, output_exp: str,
            filepath: str, line_no: int) -> None:
        self._output_filter = output_filter
        self._output_exp = output_exp
        self._filepath = filepath
        self._line_no = line_no

    @property
    def should_indent(self) -> bool:
        return False

    @property
    def should_append(self) -> bool:
        return True

    @property
    def should_unindent(self) -> bool:
        return False

    @property
    def line_no(self) -> int:
        return self._line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        splitted_stmt = stmt_str.split(" ", 1)

        stmt_keyword = splitted_stmt[0]

        if not stmt_keyword.endswith("="):
            return None

        stmt_output_filter = stmt_keyword[:-1] or "default"

        if stmt_output_filter not in Cls._filter_fn_names:
            return None

        if len(splitted_stmt) != 2:
            raise exceptions.TemplateSyntaxError(
                ("The expression to be output is empty "
                 "in file {} at line {}.").format(filepath, line_no))

        stmt_output_exp = splitted_stmt[1].strip()

        if not stmt_output_exp:
            raise exceptions.TemplateSyntaxError(
                ("The expression to be output is empty "
                 "in file {} at line {}.").format(filepath, line_no))

        return Cls(
            output_filter=stmt_output_filter,
            output_exp=stmt_output_exp,
            filepath=filepath, line_no=line_no)


class _Include(Statement):
    def __init__(self, stmt_str: str, filepath: str, line_no: int) -> None:
        self._stmt_str = stmt_str
        self._filepath = filepath
        self._line_no = line_no

    @property
    def should_indent(self) -> bool:
        return False

    @property
    def should_append(self) -> bool:
        return True

    @property
    def should_unindent(self) -> bool:
        return False

    @property
    def line_no(self) -> int:
        return self._line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        if stmt_str.split(" ", 1)[0] != "include":
            return None

        return Cls(
            stmt_str=stmt_str,
            filepath=filepath, line_no=line_no)


class _Inherit(Statement):
    def __init__(self, stmt_str: str, filepath: str, line_no: int) -> None:
        self._stmt_str = stmt_str
        self._filepath = filepath
        self._line_no = line_no

    @property
    def should_indent(self) -> bool:
        return False

    @property
    def should_append(self) -> bool:
        return True

    @property
    def should_unindent(self) -> bool:
        return False

    @property
    def line_no(self) -> int:
        return self._line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        if stmt_str.split(" ", 1)[0] != "inherit":
            return None

        return Cls(
            stmt_str=stmt_str,
            filepath=filepath, line_no=line_no)


class _Indent(Statement):
    def __init__(self, stmt_str: str, filepath: str, line_no: int) -> None:
        self._stmt_str = stmt_str
        self._filepath = filepath
        self._line_no = line_no

        self._stmts: List[Statement] = []

    def append_stmt(self, stmt: Statement) -> None:
        self._stmts.append(stmt)

    @property
    def should_indent(self) -> bool:
        return True

    @property
    def should_append(self) -> bool:
        return True

    @property
    def should_unindent(self) -> bool:
        return False

    @property
    def line_no(self) -> int:
        return self._line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        if stmt_str.split(" ", 1)[0] not in (
                "if", "with", "for", "while", "try", "async"):
            return None

        return Cls(
            stmt_str=stmt_str,
            filepath=filepath, line_no=line_no)


class _Unindent(Statement):
    @property
    def should_indent(self) -> bool:
        return False

    @property
    def should_append(self) -> bool:
        return False

    @property
    def should_unindent(self) -> bool:
        return True

    @property
    def line_no(self) -> int:
        raise NotImplementedError("This does not apply to _Unindent.")

    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        if stmt_str.split(" ", 1)[0] != "end":
            return None

        return Cls()


class _HalfIndent(Statement):
    def __init__(self, stmt_str: str, filepath: str, line_no: int) -> None:
        self._stmt_str = stmt_str
        self._filepath = filepath
        self._line_no = line_no

    @property
    def should_indent(self) -> bool:
        return True

    @property
    def should_append(self) -> bool:
        return True

    @property
    def should_unindent(self) -> bool:
        return True

    @property
    def line_no(self) -> int:
        return self._line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        if stmt_str.split(" ", 1)[0] not in (
                "else", "elif", "except", "finally"):
            return None

        return Cls(
            stmt_str=stmt_str,
            filepath=filepath, line_no=line_no)


class _Inline(Statement):
    def __init__(self, stmt_str: str, filepath: str, line_no: int) -> None:
        self._stmt_str = stmt_str
        self._filepath = filepath
        self._line_no = line_no

    @property
    def should_indent(self) -> bool:
        return False

    @property
    def should_append(self) -> bool:
        return True

    @property
    def should_unindent(self) -> bool:
        return False

    @property
    def line_no(self) -> int:
        return self._line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        if stmt_str.split(" ", 1)[0] not in (
                "break", "continue", "import", "raise", "from"):
            return None

        return Cls(
            stmt_str=stmt_str,
            filepath=filepath, line_no=line_no)


class _Comment(Statement):
    def __init__(self, cmnt_str: str, filepath: str, line_no: int) -> None:
        self._cmnt_str = cmnt_str
        self._filepath = filepath
        self._line_no = line_no

    @property
    def should_indent(self) -> bool:
        return False

    @property
    def should_append(self) -> bool:
        return True

    @property
    def should_unindent(self) -> bool:
        return False

    @property
    def line_no(self) -> int:
        return self._line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        if not stmt_str.startswith("#"):
            return None

        return Cls(
            cmnt_str=stmt_str[1:].strip(),
            filepath=filepath, line_no=line_no)


class _Code(Statement):
    def __init__(self, code_exp: str, filepath: str, line_no: int) -> None:
        self._code_exp = code_exp
        self._filepath = filepath
        self._line_no = line_no

    @property
    def should_indent(self) -> bool:
        return False

    @property
    def should_append(self) -> bool:
        return True

    @property
    def should_unindent(self) -> bool:
        return False

    @property
    def line_no(self) -> int:
        return self._line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        if not stmt_str.startswith("@ "):
            return None

        return Cls(
            code_exp=stmt_str[1:].strip(),
            filepath=filepath, line_no=line_no)


builtin_stmt_classes: Sequence[Type[Statement]] = [
    Block, _Include, _Inherit, _Indent, _Unindent, _HalfIndent, _Inline,
    _Comment, _Code]
