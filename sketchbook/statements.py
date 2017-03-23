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

from typing import List, Optional, Sequence, Type, Dict

from . import printer
from . import exceptions

import abc
import re

__all__ = [
    "Statement", "Root", "Block", "BaseOutput", "builtin_stmt_classes",
    "IndentMixIn", "AppendMixIn", "UnindentMixIn"]

_VALID_FN_NAME_RE = re.compile(r"^[a-zA-Z]([a-zA-Z0-9\_]+)?$")


def _is_valid_fn_name(maybe_fn_name: str) -> bool:
    """
    Check if this is a valid function name.
    """
    return (re.fullmatch(_VALID_FN_NAME_RE, maybe_fn_name) is not None)


class IndentMixIn(abc.ABC):
    @abc.abstractmethod
    @property
    def line_no(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def append_stmt(self, stmt: "Statement") -> None:
        raise NotImplementedError


class AppendMixIn:
    pass


class UnindentMixIn:
    pass


class Statement(abc.ABC):
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
        self._block_stmts: Dict[str, Block] = {}

    def append_stmt(self, stmt: Statement) -> None:
        self._stmts.append(stmt)

    def append_block(self, block_stmt: "Block") -> None:
        if block_stmt.block_name in self._block_stmts.keys():
            raise exceptions.BlockNameConflictError(
                f"The name of the block at {block_stmt.line_no}"
                "is conflict with the block at "
                f"{self._block_stmts[block_stmt.block_name].line_no} "
                f"in file {self._filepath}. You cannot define two block with "
                "the same name in the one file.")

        self._block_stmts[block_stmt.block_name] = block_stmt

    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        raise NotImplementedError("This does not apply to Root.")

    def print_code(self, code_printer: printer.CodePrinter) -> None:
        raise NotImplementedError


class Block(Statement, IndentMixIn, AppendMixIn):
    def __init__(self, block_name: str, filepath: str, line_no: int) -> None:
        self._block_name = block_name
        self._filepath = filepath
        self._line_no = line_no

    @property
    def block_name(self) -> str:
        return self._block_name

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
                "Invalid Block Statement. Block name expected, "
                f"got: {repr(block_name)}.")

        return Cls(
            block_name=block_name,
            filepath=filepath, line_no=line_no)


class Plain(Statement, AppendMixIn):
    def __init__(self, stmt_str: str) -> None:
        self._stmt_str = stmt_str

    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        raise NotImplementedError("This does not apply to Plain.")

    def print_code(self, code_printer: printer.CodePrinter) -> None:
        raise NotImplementedError


class BaseOutput(Statement, AppendMixIn):
    _filter_fn_names: List[str] = []

    def __init__(
        self, output_filter: str, output_exp: str,
            filepath: str, line_no: int) -> None:
        self._output_filter = output_filter
        self._output_exp = output_exp
        self._filepath = filepath
        self._line_no = line_no

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
                 f"in file {filepath} at line {line_no}."))

        stmt_output_exp = splitted_stmt[1].strip()

        if not stmt_output_exp:
            raise exceptions.TemplateSyntaxError(
                ("The expression to be output is empty "
                 f"in file {filepath} at line {line_no}."))

        return Cls(
            output_filter=stmt_output_filter,
            output_exp=stmt_output_exp,
            filepath=filepath, line_no=line_no)


class _Include(Statement, AppendMixIn):
    def __init__(self, stmt_str: str, filepath: str, line_no: int) -> None:
        self._stmt_str = stmt_str
        self._filepath = filepath
        self._line_no = line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        if stmt_str.split(" ", 1)[0] != "include":
            return None

        return Cls(
            stmt_str=stmt_str,
            filepath=filepath, line_no=line_no)


class _Inherit(Statement, AppendMixIn):
    def __init__(self, stmt_str: str, filepath: str, line_no: int) -> None:
        self._stmt_str = stmt_str
        self._filepath = filepath
        self._line_no = line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        if stmt_str.split(" ", 1)[0] != "inherit":
            return None

        return Cls(
            stmt_str=stmt_str,
            filepath=filepath, line_no=line_no)


class _Indent(Statement, IndentMixIn, AppendMixIn):
    def __init__(self, stmt_str: str, filepath: str, line_no: int) -> None:
        self._stmt_str = stmt_str
        self._filepath = filepath
        self._line_no = line_no

        self._stmts: List[Statement] = []

    def append_stmt(self, stmt: Statement) -> None:
        self._stmts.append(stmt)

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


class _Unindent(Statement, UnindentMixIn):
    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        if stmt_str.split(" ", 1)[0] != "end":
            return None

        return Cls()


class _HalfIndent(Statement, IndentMixIn, AppendMixIn, UnindentMixIn):
    def __init__(self, stmt_str: str, filepath: str, line_no: int) -> None:
        self._stmt_str = stmt_str
        self._filepath = filepath
        self._line_no = line_no

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


class _Inline(Statement, AppendMixIn):
    def __init__(self, stmt_str: str, filepath: str, line_no: int) -> None:
        self._stmt_str = stmt_str
        self._filepath = filepath
        self._line_no = line_no

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


class _Comment(Statement, AppendMixIn):
    def __init__(self, cmnt_str: str, filepath: str, line_no: int) -> None:
        self._cmnt_str = cmnt_str
        self._filepath = filepath
        self._line_no = line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, filepath: str,
            line_no: int) -> Optional["Statement"]:
        if not stmt_str.startswith("#"):
            return None

        return Cls(
            cmnt_str=stmt_str[1:].strip(),
            filepath=filepath, line_no=line_no)


class _Code(Statement, AppendMixIn):
    def __init__(self, code_exp: str, filepath: str, line_no: int) -> None:
        self._code_exp = code_exp
        self._filepath = filepath
        self._line_no = line_no

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
