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

from typing import Optional, List

from . import statements
from . import template
from . import exceptions

import io

__all__ = ["TemplateParser"]


class _ReadFinished(Exception):
    pass


class TemplateParser:
    """
    The one-time, non-reusable template parser.
    """
    def __init__(self, tpl: "template.Template") -> None:
        self._tpl = tpl
        self._tpl_ctx = self._tpl._tpl_ctx

        self._io = io.StringIO(self._tpl._tpl_content)

        self._current_line_no = 0
        self._current_line = ""

        self._root = statements.Root(filepath=self._tpl._path)
        self._indents: List[statements.IndentMixIn] = []

        self._parse()

    def _move_to_next_line(self) -> None:
        assert not self._current_line, \
            ("Parsing of the last line is not completed "
             f"in file {self._tpl._path} at line {self._current_line_no}.")

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

        for StmtCls in self._tpl_ctx.stmt_classes:
            maybe_stmt = StmtCls.try_match(
                stmt_str, filepath=self._tpl._path, line_no=line_no)

            if maybe_stmt is None:
                continue

            return maybe_stmt

        else:
            raise exceptions.UnknownStatementError(
                f"Unknown Statement {repr(stmt_str)} "
                f"in file {self._tpl._path} at line {line_no}.")

    def _find_next_stmt(self) -> "statements.Statement":
        stmt_chunks: List[str] = []
        begin_mark_line_no = -1

        while True:
            if not self._current_line:
                try:
                    self._move_to_next_line()

                except _ReadFinished:
                    if begin_mark_line_no != -1:
                        raise exceptions.TemplateSyntaxError(
                            ("Cannot find end mark for begin mark "
                             f"in file {self._tpl._path} "
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
            raise exceptions.TemplateSyntaxError(
                "Redundant Unindent Statement "
                f"in file {self._tpl._path} at line {self._current_line_no}.")

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
            raise exceptions.TemplateSyntaxError(
                "Unindented Indent Statement "
                f"in file {self._tpl._path} "
                f"at line {self._indents[-1].line_no}.")

    @classmethod
    def parse_tpl(Cls, tpl: "template.Template") -> "statements.Root":
        tpl_parser = Cls(tpl)
        return tpl_parser.root
