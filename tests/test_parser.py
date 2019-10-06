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

from sketchbook import Sketch, SketchSyntaxError, UnknownStatementError

import pytest
import os

_TEST_CURIO = True if bool(os.environ.get("TEST_CURIO", False)) else False

if _TEST_CURIO:
    from sketchbook.testutils import CurioTestHelper
    from sketchbook import CurioSketchContext

    helper = CurioTestHelper(__file__)

    default_skt_ctx = CurioSketchContext()

else:
    from sketchbook.testutils import AsyncioTestHelper
    from sketchbook import AsyncioSketchContext

    helper = AsyncioTestHelper(__file__)

    default_skt_ctx = AsyncioSketchContext()


class StatementEscapeTestCase:
    @helper.force_sync
    async def test_stmts_escape(self) -> None:
        skt = Sketch(
            "<%% is the begin mark, and <%r= \"%%> is the end mark. \" %>"
            "<%r= \"<% and\" %> %> only need to be escaped whenever they "
            "have ambiguity of the templating system.",
            skt_ctx=default_skt_ctx)

        assert await skt.draw() == (
            "<% is the begin mark, and %> is the end mark. "
            "<% and %> only need to be escaped whenever they "
            "have ambiguity of the templating system.")

    @helper.force_sync
    async def test_multiline_stmts(self) -> None:
        skt = Sketch(
            """\
<% if a == \
            True
%>
Hello, it's me!
<% else %>
No, it's not me!
<% end %>""",
            skt_ctx=default_skt_ctx)

        assert await skt.draw(a=True) == "\nHello, it's me!\n"
        assert await skt.draw(a=False) == "\nNo, it's not me!\n"


class MalformedSketchTestCase:
    def test_malformed_stmts(self) -> None:
        with pytest.raises(SketchSyntaxError):
            Sketch("<% <%", skt_ctx=default_skt_ctx)

    def test_missing_end_mark(self) -> None:
        with pytest.raises(SketchSyntaxError):
            Sketch("<% while True %>", skt_ctx=default_skt_ctx)

    def test_redundant_end_mark(self) -> None:
        with pytest.raises(SketchSyntaxError):
            Sketch("<% if False %><% end %><% end %>", skt_ctx=default_skt_ctx)

    def test_unknown_stmt(self) -> None:
        with pytest.raises(UnknownStatementError):
            Sketch("<% if anyways %><% fi %>", skt_ctx=default_skt_ctx)
