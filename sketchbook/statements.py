#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   Copyright 2019 Kaede Hoshikawa
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
from . import sketch

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
    def append_stmt(self, stmt: "AppendMixIn") -> None:  # pragma: no cover
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def line_no(self) -> int:  # pragma: no cover
        raise NotImplementedError


class AppendMixIn(abc.ABC):
    @property
    @abc.abstractmethod
    def line_no(self) -> int:  # pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    def print_code(
        self, py_printer: printer.PythonPrinter) -> \
            None:  # pragma: no cover
        raise NotImplementedError


class UnindentMixIn(abc.ABC):
    pass


class Statement(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def try_match(
        Cls, stmt_str: str, skt: sketch.Sketch,
            line_no: int) -> Optional["Statement"]:  # pragma: no cover
        raise NotImplementedError


class Root(Statement, AppendMixIn):
    def __init__(self, skt: sketch.Sketch) -> None:
        self._skt = skt

        self._stmts: List[AppendMixIn] = []
        self._block_stmts: Dict[str, Block] = {}

    @property
    def line_no(self) -> int:
        return 0

    def append_stmt(self, stmt: AppendMixIn) -> None:
        self._stmts.append(stmt)

    def append_block(self, block_stmt: "Block") -> None:
        if block_stmt.block_name in self._block_stmts.keys():
            raise exceptions.BlockNameConflictError(
                f"The name of the block at {block_stmt.line_no}"
                "conflicts with the block at "
                f"{self._block_stmts[block_stmt.block_name].line_no} "
                f"in file {self._skt._path}. You cannot define two blocks "
                "with the same name in the one file.")

        self._block_stmts[block_stmt.block_name] = block_stmt

    @classmethod
    def try_match(
        Cls, stmt_str: str, skt: sketch.Sketch,
            line_no: int) -> Optional["Statement"]:  # pragma: no cover
        raise NotImplementedError("This does not apply to Root.")

    def print_code(self, py_printer: printer.PythonPrinter) -> None:
        py_printer.writeline("import sketchbook")
        py_printer.writeline("_SKT_BLOCK_RUNTIMES = {}")

        for block_stmt in self._block_stmts.values():
            block_stmt.print_block_code(py_printer)

        py_printer.writeline(
            "class _SktCurrentRuntime(sketchbook.SketchRuntime):", self)
        with py_printer.indent_block():
            py_printer.writeline(
                "_BLOCK_RUNTIMES = _SKT_BLOCK_RUNTIMES", self)

            py_printer.writeline(
                "async def _draw_body(self) -> None:", self)
            with py_printer.indent_block():
                for stmt in self._stmts:
                    stmt.print_code(py_printer)


class Block(Statement, IndentMixIn, AppendMixIn):
    def __init__(
            self, block_name: str, skt: sketch.Sketch, line_no: int) -> None:
        self._block_name = block_name
        self._skt = skt
        self._line_no = line_no

        self._stmts: List[AppendMixIn] = []

    def append_stmt(self, stmt: AppendMixIn) -> None:
        self._stmts.append(stmt)

    @property
    def block_name(self) -> str:
        return self._block_name

    @property
    def line_no(self) -> int:
        return self._line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, skt: sketch.Sketch,
            line_no: int) -> Optional["Statement"]:
        splitted_stmt = stmt_str.split(" ", 1)
        if splitted_stmt[0] != "block":
            return None

        if len(splitted_stmt) != 2 or (not splitted_stmt[1].strip()):
            raise exceptions.SketchSyntaxError(
                "Block name cannot be empty.")

        block_name = splitted_stmt[1].strip()

        if not _is_valid_fn_name(block_name):
            raise exceptions.SketchSyntaxError(
                "Invalid Block Statement. Block name expected, "
                f"got: {repr(block_name)}.")

        return Cls(
            block_name=block_name,
            skt=skt, line_no=line_no)

    def print_code(self, py_printer: printer.PythonPrinter) -> None:
        py_printer.writeline(
            f"self.write(await self.blocks[{repr(self.block_name)}, True](), "
            "escape=\"raw\")",
            self)

    def print_block_code(self, py_printer: printer.PythonPrinter) -> None:
        py_printer.writeline(
            "class _SktCurrentBlockRuntime(sketchbook.BlockRuntime):",
            self)
        with py_printer.indent_block():
            py_printer.writeline(
                "async def _draw_block(self) -> None:", self)
            with py_printer.indent_block():
                for stmt in self._stmts:
                    stmt.print_code(py_printer)

        py_printer.writeline(
            f"_SKT_BLOCK_RUNTIMES[{self.block_name!r}] = "
            "_SktCurrentBlockRuntime")


class Plain(Statement, AppendMixIn):
    def __init__(self, plain_str: str) -> None:
        self._plain_str = plain_str

    @property
    def line_no(self) -> int:  # pragma: no cover
        raise NotImplementedError("This does not apply to Plain.")

    @classmethod
    def try_match(
        Cls, stmt_str: str, skt: sketch.Sketch,
            line_no: int) -> Optional["Statement"]:  # pragma: no cover
        raise NotImplementedError("This does not apply to Plain.")

    def print_code(self, py_printer: printer.PythonPrinter) -> None:
        py_printer.writeline(
            f"self.write({repr(self._plain_str)}, escape=\"raw\")")


class BaseOutput(Statement, AppendMixIn):
    _filter_fn_names: List[str] = []

    def __init__(
        self, output_filter: str, output_exp: str,
            skt: sketch.Sketch, line_no: int) -> None:
        self._output_filter = output_filter
        self._output_exp = output_exp
        self._skt = skt
        self._line_no = line_no

    @property
    def line_no(self) -> int:
        return self._line_no

    @classmethod
    def try_match(
            Cls, stmt_str: str, skt: sketch.Sketch,
            line_no: int) -> Optional["Statement"]:
        splitted_stmt = stmt_str.split(" ", 1)

        stmt_keyword = splitted_stmt[0]

        if not stmt_keyword.endswith("="):
            return None

        stmt_output_filter = stmt_keyword[:-1] or "default"

        if stmt_output_filter not in Cls._filter_fn_names:
            return None

        if len(splitted_stmt) != 2:
            raise exceptions.SketchSyntaxError(
                ("Output content is empty "
                 f"in file {skt._path} at line {line_no}."))

        stmt_output_exp = splitted_stmt[1].strip()

        if not stmt_output_exp:
            raise exceptions.SketchSyntaxError(
                ("The expression to be output is empty "
                 f"in file {skt._path} at line {line_no}."))

        return Cls(
            output_filter=stmt_output_filter,
            output_exp=stmt_output_exp,
            skt=skt, line_no=line_no)

    def print_code(self, py_printer: printer.PythonPrinter) -> None:
        py_printer.writeline(
            f"self.write({self._output_exp}, "
            f"escape={self._output_filter!r})")


class _Include(Statement, AppendMixIn):
    def __init__(
            self, target_path: str, skt: sketch.Sketch, line_no: int) -> None:
        self._target_path = target_path
        self._skt = skt
        self._line_no = line_no

    @property
    def line_no(self) -> int:
        return self._line_no

    @classmethod
    def try_match(
            Cls, stmt_str: str, skt: sketch.Sketch,
            line_no: int) -> Optional["Statement"]:

        splitted_stmt = stmt_str.split(" ", 1)
        if splitted_stmt[0] != "include":
            return None

        if len(splitted_stmt) < 2:
            raise exceptions.SketchSyntaxError(
                f"Invalid syntax in file {skt._path} at line {line_no}, "
                "you must provide the path to be included.")

        return Cls(
            target_path=splitted_stmt[1],
            skt=skt, line_no=line_no)

    def print_code(self, py_printer: printer.PythonPrinter) -> None:
        py_printer.writeline(
            "self.write(await "
            f"self._include_sketch({self._target_path}), escape=\"raw\")",
            self)


class _Inherit(Statement, AppendMixIn):
    def __init__(
            self, target_path: str, skt: sketch.Sketch, line_no: int) -> None:
        self._target_path = target_path
        self._skt = skt
        self._line_no = line_no

    @property
    def line_no(self) -> int:
        return self._line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, skt: sketch.Sketch,
            line_no: int) -> Optional["Statement"]:
        splitted_stmt = stmt_str.split(" ", 1)
        if splitted_stmt[0] != "inherit":
            return None

        if len(splitted_stmt) < 2:
            raise exceptions.SketchSyntaxError(
                f"Invalid syntax in file {skt._path} at line {line_no}, "
                "you must provide the path to be inherited.")

        return Cls(
            target_path=splitted_stmt[1],
            skt=skt, line_no=line_no)

    def print_code(self, py_printer: printer.PythonPrinter) -> None:
        py_printer.writeline(
            f"await self._add_parent({self._target_path})", self)


class _Indent(Statement, IndentMixIn, AppendMixIn):
    def __init__(
            self, stmt_str: str, skt: sketch.Sketch, line_no: int) -> None:
        self._stmt_str = stmt_str
        self._skt = skt
        self._line_no = line_no

        self._stmts: List[AppendMixIn] = []

    def append_stmt(self, stmt: AppendMixIn) -> None:
        self._stmts.append(stmt)

    @property
    def line_no(self) -> int:
        return self._line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, skt: sketch.Sketch,
            line_no: int) -> Optional["Statement"]:
        if stmt_str.split(" ", 1)[0] not in (
                "if", "with", "for", "while", "try", "async"):
            return None

        return Cls(
            stmt_str=stmt_str.strip(),
            skt=skt, line_no=line_no)

    def print_code(self, py_printer: printer.PythonPrinter) -> None:
        py_printer.writeline(f"{self._stmt_str}:", self)

        with py_printer.indent_block():
            for stmt in self._stmts:
                stmt.print_code(py_printer)

            py_printer.writeline("pass", self)


class _Unindent(Statement, UnindentMixIn):
    @classmethod
    def try_match(
        Cls, stmt_str: str, skt: sketch.Sketch,
            line_no: int) -> Optional["Statement"]:
        if stmt_str.split(" ", 1)[0] != "end":
            return None

        return Cls()


class _HalfIndent(Statement, IndentMixIn, AppendMixIn, UnindentMixIn):
    def __init__(
            self, stmt_str: str, skt: sketch.Sketch, line_no: int) -> None:
        self._stmt_str = stmt_str
        self._skt = skt
        self._line_no = line_no

        self._stmts: List[AppendMixIn] = []

    def append_stmt(self, stmt: AppendMixIn) -> None:
        self._stmts.append(stmt)

    @property
    def line_no(self) -> int:
        return self._line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, skt: sketch.Sketch,
            line_no: int) -> Optional["Statement"]:
        if stmt_str.split(" ", 1)[0] not in (
                "else", "elif", "except", "finally"):
            return None

        return Cls(
            stmt_str=stmt_str.strip(),
            skt=skt, line_no=line_no)

    def print_code(self, py_printer: printer.PythonPrinter) -> None:
        py_printer.writeline(f"{self._stmt_str}:", self)

        with py_printer.indent_block():
            for stmt in self._stmts:
                stmt.print_code(py_printer)

            py_printer.writeline("pass", self)


class _Inline(Statement, AppendMixIn):
    def __init__(
            self, stmt_str: str, skt: sketch.Sketch, line_no: int) -> None:
        self._stmt_str = stmt_str
        self._skt = skt
        self._line_no = line_no

    @property
    def line_no(self) -> int:
        return self._line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, skt: sketch.Sketch,
            line_no: int) -> Optional["Statement"]:
        if stmt_str.split(" ", 1)[0] not in (
            "break", "continue", "import", "raise", "from",
                "nonlocal", "global", "assert"):
            return None

        return Cls(
            stmt_str=stmt_str.strip(),
            skt=skt, line_no=line_no)

    def print_code(self, py_printer: printer.PythonPrinter) -> None:
        py_printer.writeline(self._stmt_str, self)


class _Comment(Statement, AppendMixIn):
    def __init__(
            self, cmnt_str: str, skt: sketch.Sketch, line_no: int) -> None:
        self._cmnt_str = cmnt_str
        self._skt = skt
        self._line_no = line_no

    @property
    def line_no(self) -> int:
        return self._line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, skt: sketch.Sketch,
            line_no: int) -> Optional["Statement"]:
        if not stmt_str.startswith("#"):
            return None

        return Cls(
            cmnt_str=stmt_str[1:].strip(),
            skt=skt, line_no=line_no)

    def print_code(self, py_printer: printer.PythonPrinter) -> None:
        for cmnt_line in self._cmnt_str.splitlines():
            py_printer.writeline(f"# {cmnt_line}", self)


class _Assign(Statement, AppendMixIn):
    def __init__(
        self, target_lst: str, exp: str, skt: sketch.Sketch,
            line_no: int) -> None:
        self._target_lst = target_lst
        self._exp = exp

        self._skt = skt
        self._line_no = line_no

    @property
    def line_no(self) -> int:
        return self._line_no

    @classmethod
    def try_match(
        Cls, stmt_str: str, skt: sketch.Sketch,
            line_no: int) -> Optional["Statement"]:
        stmt_str = stmt_str.strip()
        if not stmt_str.startswith("let "):
            return None

        assign_stmt = stmt_str[4:]

        try:
            target_lst, exp = assign_stmt.split("=", 1)

        except (ValueError, TypeError) as e:
            raise exceptions.SketchSyntaxError(
                f"Invaild assignment statment at line {line_no} "
                f"in file {skt._path}.") from e

        return Cls(
            target_lst=target_lst.strip(),
            exp=exp.strip(),
            skt=skt, line_no=line_no)

    def print_code(self, py_printer: printer.PythonPrinter) -> None:
        py_printer.writeline(f"{self._target_lst} = {self._exp}", self)


builtin_stmt_classes: Sequence[Type[Statement]] = [
    Block, _Include, _Inherit, _Indent, _Unindent, _HalfIndent, _Inline,
    _Comment, _Assign]
