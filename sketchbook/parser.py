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

from typing import List

from . import statements
from . import exceptions

import io
import typing

if typing.TYPE_CHECKING:
    from . import sketch  # noqa: F401

__all__ = ["SketchParser"]


class _ReadFinished(Exception):
    pass


class SketchParser:
    """
    The one-time, non-reusable sketch parser.
    """
    def __init__(self, __skt: "sketch.Sketch") -> None:
        self._skt = __skt
        self._ctx = self._skt._ctx

        self._io = io.StringIO(self._skt._content)

        self._current_line_no = 0
        self._current_line = ""

        self._root = statements.Root(skt=self._skt)
        self._indents: List[statements.IndentMixIn] = []

        self._parse()

    def _move_to_next_line(self) -> None:
        assert not self._current_line, \
            ("Parsing of the last line is not completed "
             f"in file {self._skt._path} at line {self._current_line_no}.")

        new_line = self._io.readline()

        if not new_line:
            raise _ReadFinished

        self._current_line_no += 1
        self._current_line = new_line

    @property
    def root(self) -> "statements.Root":
        return self._root

    def _find_next_begin_mark(self) -> int:
        start_pos = 0

        while True:
            pos = self._current_line.find("<%", start_pos)

            if pos == -1:
                return -1

            elif self._current_line[pos + 2:].startswith("%"):
                start_pos = pos + 2
                end_pos = start_pos + 1

                self._current_line = (
                    self._current_line[:start_pos] +
                    self._current_line[end_pos:])

                continue

            else:
                return pos

    def _find_next_end_mark(self) -> int:
        start_pos = 0

        while True:
            pos = self._current_line.find("%>", start_pos)

            if pos == -1:
                return -1

            elif pos == 0:
                return 0

            elif self._current_line[:pos].endswith("%"):
                start_pos = pos - 1
                end_pos = pos

                self._current_line = (
                    self._current_line[:start_pos] +
                    self._current_line[end_pos:])

                start_pos = pos + 1

                continue

            else:
                return pos

    def _parse_stmt(
            self, stmt_str: str, line_no: int) -> "statements.Statement":
        stmt_str = stmt_str.strip()

        if stmt_str.endswith(":"):
            raise exceptions.SketchSyntaxError(
                    "A Statement Cannot be Finished with `:`, "
                    "use `<% end %>` instead. For detailed information, "
                    "please see the documation.")

        for StmtCls in self._ctx.stmt_classes:
            maybe_stmt = StmtCls.try_match(
                stmt_str, skt=self._skt, line_no=line_no)

            if maybe_stmt is None:
                continue

            return maybe_stmt

        else:
            raise exceptions.UnknownStatementError(
                f"Unknown Statement {repr(stmt_str)} "
                f"in file {self._skt._path} at line {line_no}.")

    def _find_next_stmt(self) -> "statements.Statement":
        stmt_chunks: List[str] = []
        begin_mark_line_no = -1

        while True:
            if not self._current_line:
                try:
                    self._move_to_next_line()

                except _ReadFinished:
                    if begin_mark_line_no != -1:
                        raise exceptions.SketchSyntaxError(
                            ("Cannot find end mark for begin mark "
                             f"in file {self._skt._path} "
                             f"at line {begin_mark_line_no}."))

                    elif stmt_chunks:
                        return statements.Plain("".join(stmt_chunks))

                    else:
                        raise

            if begin_mark_line_no == -1:
                begin_mark_pos = self._find_next_begin_mark()

                if begin_mark_pos == -1:
                    stmt_chunks.append(self._current_line)
                    self._current_line = ""

                    continue

                elif begin_mark_pos > 0:
                    stmt_chunks.append(self._current_line[:begin_mark_pos])
                    self._current_line = self._current_line[begin_mark_pos:]

                    return statements.Plain("".join(stmt_chunks))

                elif stmt_chunks:
                    return statements.Plain("".join(stmt_chunks))

                begin_mark_line_no = self._current_line_no
                self._current_line = self._current_line[2:]

            end_mark_pos = self._find_next_end_mark()

            if end_mark_pos == -1:
                stmt_chunks.append(self._current_line)
                self._current_line = ""

                continue

            stmt_chunks.append(self._current_line[:end_mark_pos])
            self._current_line = self._current_line[end_mark_pos + 2:]

            return self._parse_stmt("".join(stmt_chunks), begin_mark_line_no)

    def _append_to_current(self, stmt: "statements.AppendMixIn") -> None:
        if self._indents:
            self._indents[-1].append_stmt(stmt)

        else:
            self._root.append_stmt(stmt)

    def _unindent_current(self) -> None:
        if self._indents:
            self._indents.pop()

        else:
            raise exceptions.SketchSyntaxError(
                "Redundant Unindent Statement "
                f"in file {self._skt._path} at line {self._current_line_no}.")

    def _parse(self) -> None:
        while True:
            try:
                stmt = self._find_next_stmt()

            except _ReadFinished:
                break

            if isinstance(stmt, statements.UnindentMixIn):
                self._unindent_current()

            if isinstance(stmt, statements.AppendMixIn):
                self._append_to_current(stmt)

            if isinstance(stmt, statements.IndentMixIn):
                self._indents.append(stmt)

            if isinstance(stmt, statements.Block):
                self._root.append_block(stmt)

        if self._indents:
            raise exceptions.SketchSyntaxError(
                "Unindented Indent Statement "
                f"in file {self._skt._path} "
                f"at line {self._indents[-1].line_no}.")

    @classmethod
    def parse_sketch(Cls, skt: "sketch.Sketch") -> "statements.Root":
        skt_parser = Cls(skt)
        return skt_parser.root
